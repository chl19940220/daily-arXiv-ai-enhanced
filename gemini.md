# 项目名称：daily-arxiv-ai-enhanced

## 1. 项目概述 (Project Overview)

本项目是一个python语言编写的从arxiv上获取感兴趣的论文并调用LLM进行总结的项目，可以通过github action每日自动运行。

其核心功能包括：

- 功能点A：从arxiv上按照分类、关键词爬取最新论文
- 功能点B：调用LLM服务对论文进行总结，形成结构化数据
- 功能点C：将结构化数据保存至本地，并上传到github空间

## 2. 项目结构 (Project Structure)

. github:定义github action的workflow

.specstory: 保存cursor对话，这部分是你无需关注的

ai:调用LLM的核心逻辑

daily_arxiv:从arxiv上爬取论文数据的核心逻辑

data:以前保存的论文数据

to_md:将数据保存为markdown格式

## 3.需求

1. arxiv数据爬取

   根据分类和keywords爬取前一天的论文，避免重复

2. AI功能：

   1.1 支持Gemini模型，支持兼容openAI接口的模型，base_url和api_key以及model_name都从环境变量中读取

   1.2 将所有提示词都改为中文，总结论文时只参考论文标题和摘要

3. 保存

   3.1格式化文档：将论文存成一个Paper对象，包含这些属性：

   ​     Title：论文标题，与爬取到的论文标题保持一致

   ​    Authors：只列出最多两个作者名字

   ​    Institution：第一作者所在学校/单位

      Summary：AI总结后的论文信息

     URL:论文的arxiv链接

   3.2 保存：

   将每一个Paper对象按markdown格式输出，Title为二级标题，其余字段为三级标题

   将上面的markdown格式的Paper信息存到notion中。之前的项目时保存在本地，现在要改为不保存任何文件在本地，而是通过notion来保存。我已经在notion中创建了新的集成，名称为Arxiv Daily Papers，在notion上创建了新的页面，名称为Arxiv Daily Papers，且已经将它与集成相关联

4. github workflow

   设置在每日的北京时间凌晨3点半执行workflow。以上环境变量中llm的api_key，notion key都需要在github的仓库“Settings"-"Secrets and variables"-"Actions"-“Secrets”中配置，代码也需要从这里读取key。llm的base_url/model_name，爬取论文时设置的keywords、分类、每个分类下每日最多爬取的论文数量、notion仓库等信息都在Settings"-"Secrets and variables"-"Actions"-"Variables"中配置并读取。

   