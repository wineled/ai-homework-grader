# AI作业批改师

基于 Claude API 的智能数学作业批改工具。

## 功能

- ✅ 自动批改数学作业
- ✅ 生成详细批改结果（XML格式）
- ✅ 支持多题目批改
- ✅ 交互模式 / 文件模式 / JSON模式

## 安装

```bash
pip install -r requirements.txt
```

## 配置

设置环境变量：

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

或创建 `.env` 文件：

```
ANTHROPIC_API_KEY=your-api-key
```

## 使用方法

### 1. 交互模式

```bash
python main.py -i
```

按提示输入题目和学生作答，输入 `done` 开始批改。

### 2. 文件模式

创建作业文件 `homework.txt`：

```
题目：计算 2 + 3 = ?
答案：5

题目：求方程 x + 2 = 5 的解
答案：x = 4
```

运行：

```bash
python main.py -f homework.txt
```

### 3. JSON模式

```bash
python main.py -j '{"subject":"数学","items":[{"question":"计算 2+3=?","answer":"5"},{"question":"求x+2=5的解","answer":"x=4"}]}'
```

### 4. 命令行参数

| 参数 | 说明 |
|------|------|
| `-i, --interactive` | 交互模式 |
| `-f, --file` | 作业文件路径 |
| `-j, --json` | JSON格式数据 |
| `-s, --subject` | 科目（默认：数学） |
| `-m, --model` | 模型（默认：claude-sonnet-4-20250514） |
| `-k, --api-key` | API Key |

## 输出格式

```xml
<root>
<item>
<题目要求> 计算 2 + 3 = ? </题目要求>
<参考答案> 5 </参考答案>
<作答内容> 5 </作答内容>
<批改结果> 正确 </批改结果>
</item>
</root>
```

## 示例

### 输入

```
题目：一个长方形的长是8厘米，宽是5厘米，求它的周长和面积。
学生作答：周长=26厘米，面积=40平方厘米
```

### 输出

```xml
<root>
<item>
<题目要求> 求长方形周长（长8cm，宽5cm） </题目要求>
<参考答案> 周长 = 2×(8+5) = 26厘米 </参考答案>
<作答内容> 周长=26厘米 </作答内容>
<批改结果> 正确 </批改结果>
</item>
<item>
<题目要求> 求长方形面积（长8cm，宽5cm） </题目要求>
<参考答案> 面积 = 8×5 = 40平方厘米 </参考答案>
<作答内容> 面积=40平方厘米 </作答内容>
<批改结果> 正确 </批改结果>
</item>
</root>
```

## 扩展

可以修改 `SYSTEM_PROMPT` 来支持其他科目（语文、英语、物理等）。

## License

MIT
