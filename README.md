# video-from-audio-webp

计划输入一段音频，自动生成字幕并根据字幕配图，最终合成一个视频，目前可以成片。

实现时将视频处理的每个步骤写成一个可插拔的流水线类，方便以后更改需求。

参考资料：
- Scrapy 的 PipelineManager 类
- Django 的 BaseCommand 类
- [Automatically making YouTube videos with Google Images](https://www.youtube.com/watch?v=Jr9sptoLvJU)
