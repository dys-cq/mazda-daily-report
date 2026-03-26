import re, json
path = r'C:\\Users\\Administrator\\.openclaw\\workspace\\miaoda-test-apps.md'
apps=[]
with open(path,encoding='utf-8') as f:
    lines=f.readlines()

name=None
fields={}
for line in lines:
    if line.startswith('### '):
        # only accept numbered items like "### 1. 标题"
        title=line.strip()[4:]
        if not re.match(r'^\d+\.', title):
            continue
        if name:
            apps.append((name, fields))
        name=title
        fields={}
    elif name and line.strip().startswith('- **'):
        m=re.match(r'- \*\*(.+?)\*\*：(.+)', line.strip())
        if m:
            fields[m.group(1)]=m.group(2)

if name:
    apps.append((name, fields))

print('count', len(apps))

out=[]
for name, flds in apps:
    prompt = f"创建一个名为『{name}』的心理/趣味测试应用。要求：1) 测试维度：{flds.get('测试维度','')}; 2) 题目数量：{flds.get('题目数量','')}; 3) 结果输出：{flds.get('结果输出','')}; 4) 分享功能：{flds.get('分享功能','')}; 5) 标准流程：首页介绍→答题页(单题+进度条)→生成页→结果页(含分享按钮)。风格：适合小红书分享，清新简洁。"
    out.append({'name':name,'prompt':prompt})

out_path = r'C:\\Users\\Administrator\\.openclaw\\workspace\\miaoda_app_prompts.json'
with open(out_path,'w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print('saved', out_path)
