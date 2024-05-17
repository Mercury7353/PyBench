# codeinterpreterBenchmark



## 自建评测集和评测脚本
包含Image Bench和Data Bench两部分
0515 目前 Image Bench已经完成

### ImageBench  
其中，test_vllm是测试本机通过部署的模型的脚本。
test_codeact和testtest_function call 分别是测试llmcenter模型的两种方法的脚本  

已有的图片数据和轨迹数据同样在文件夹中

## 0517 update.   
Complete ImageBench and DataBench. 
Currently, DataBench is totally evaluated by gpt-4(Given trajectory). 
While the PassRate of ImageBench is evaluted by myself...  Quality is evaluated by gpt-4
