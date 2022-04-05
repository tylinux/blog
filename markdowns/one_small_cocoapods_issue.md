# CocoaPods 小坑一例

## 错误信息

```
[!] The 'Pods-xxx' target has libraries with conflicting names: libflipper-rsocket.a.
```

## 背景信息

公司使用的是二进制化后的 pod，podspec 中使用 `vendored_libraries` 引入了 `libFlipper-RSocket.a`，然而在 `pod install` 的时候，出现了如上的错误，搜索一下，别人出现这个问题是两个不同的 pod 引用了相同的 .a 文件。但是我可以肯定我这里是没有这个问题的。

## 排查

根据报错的信息，找到源码位置：`lib/cocoapods/installer/xcode/target_validator.rb`，如下：

```ruby
def verify_no_duplicate_framework_and_library_names
  aggregate_targets.each do |aggregate_target|
    aggregate_target.user_build_configurations.each_key do |config|
      pod_targets = aggregate_target.pod_targets_for_build_configuration(config)
      file_accessors = pod_targets.flat_map(&:file_accessors).select { |fa| fa.spec.library_specification? }

      frameworks = file_accessors.flat_map(&:vendored_frameworks).uniq.map(&:basename)
      frameworks += pod_targets.select { |pt| pt.should_build? && pt.build_as_framework? }.map(&:product_module_name).uniq
      verify_no_duplicate_names(frameworks, aggregate_target.label, "frameworks")

      libraries = file_accessors.flat_map(&:vendored_libraries).uniq.map(&:basename)
      libraries += pod_targets.select { |pt| pt.should_build? && pt.build_as_library? }.map(&:product_name)
      verify_no_duplicate_names(libraries, aggregate_target.label, "libraries")
    end
  end
end

def verify_no_duplicate_names(names, label, type)
  duplicates = names.group_by { |n| n.to_s.downcase }.select { |_, v| v.size > 1 }.keys
  unless duplicates.empty?
    raise Informative, "The '#{label}' target has " \
          "#{type} with conflicting names: #{duplicates.to_sentence}."
  end
end
```

重点是如下几行：

```ruby
# 获取所有 pod 里的 vendored_libraries
libraries = file_accessors.flat_map(&:vendored_libraries).uniq.map(&:basename)

# 再拼上所有需要编译生成 .a 的
libraries += pod_targets.select { |pt| pt.should_build? && pt.build_as_library? }.map(&:product_name)

# 验证有没有同名的
verify_no_duplicate_names(libraries, aggregate_target.label, "libraries")
```

通过断点发现了问题， `libFlipper-RSocket.a` 即在 `vendored_libraries` 里，也在需要编译的 .a 里，但是筛查 `Pods/Flipper-RSocket` 目录下也没有需要编译的文件，这是怎么回事?

排查思路很明确， 看看 `should_build` 为什么会是 true。 找到给 `.should_build` 赋值的地方：`lib/cocoapods/target/pod_target.rb:280`:

```ruby
def should_build?
  return @should_build if defined? @should_build
  accessors = file_accessors.select { |fa| fa.spec.library_specification? }
  source_files = accessors.flat_map(&:source_files)
  source_files -= accessors.flat_map(&:headers)
  @should_build = !source_files.empty?
end
```

OK, source_file 目录下的文件，除去头文件，如果剩下的不为空，should_build 就为 true。 下面来看 `Flipper-RSocket.podspec` 里 source_files  是怎么定义的：

```ruby
spec.source_files = ["rsocket/benchmarks/*",
                       "rsocket/framing/*",
                       "rsocket/internal/*",
                       "rsocket/statemachine/*",
                       "rsocket/transports/*",
                       "rsocket/transports/**/*",
                       "yarpl/observable/*",
                       "yarpl/flowable/*",
                       "rsocket/*"]                     
```

问题出在了 `/*` 上，在 `rsocket/benchmarks/` 目录下，除了源文件和头文件之外，还有 `CMakeLists.txt` 和 `README.md` 文件，导致判断 `source_files` 不为空，should_build 就为 true 了。

## 解决方案

有几个方案，一是 `source_files` 中只包含常见源码和头文件类型，如下：

```ruby
spec.source_files = [
    "rsocket/benchmarks/*.{h,hpp,c,cpp,mm,m}",
    "rsocket/framing/*.{h,hpp,c,cpp,mm,m}",
    "rsocket/internal/*.{h,hpp,c,cpp,mm,m}",
    "rsocket/statemachine/*.{h,hpp,c,cpp,mm,m}",
    "rsocket/transports/*.{h,hpp,c,cpp,mm,m}",
    "rsocket/transports/**/*.{h,hpp,c,cpp,mm,m}",
    "yarpl/observable/*.{h,hpp,c,cpp,mm,m}",
    "yarpl/flowable/*.{h,hpp,c,cpp,mm,m}",
    "rsocket/*.{h,hpp,c,cpp,mm,m}",
]
```

二是 exclude 掉 `.txt` 和 `.md` 文件，如下：

```ruby
spec.exclude_files = [
  "rsocket/**/*.{txt,md}"
]
```
