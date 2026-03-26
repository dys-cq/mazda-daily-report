import json

# API 返回的完整结果
api_response = {
  "code": 0,
  "msg": "",
  "data": "{\"sellpoints\":\"{\\\"检查结果分析\\\":\\\"### 1. 产品全称\\\\n酷洛菲黑松露润浸洁面乳 (Black Truffle Moisturizing Facial Cleanser)\\\\n\\\\n### 2. 成分亮点\\\\n* **主要功效成分**: 黑孢块菌（TUBER MELANOSPORUM）提取物、甘油、透明质酸钠、积雪草（CENTELLA ASIATICA）叶提取物、多种保湿成分\\\\n* **全成分列表**:\\\\n水、甘油、月桂醇聚醚硫酸酯钠、月桂酰肌氨酸钠、椰油酰胺丙基甜菜碱、硬脂酸、PEG-120 甲基葡萄糖二油酸酯、PEG-150 二硬脂酸酯、氯化钠、羟丙基甲基纤维素、苯氧乙醇、香精\\\\n微量成分：黑孢块菌（TUBER MELANOSPORUM）提取物、透明质酸钠、山嵛酸、聚季铵盐、透明质酸钠、甲基丙二醇、积雪草（CENTELLA ASIATICA）叶提取物、泛醇、甲基丙二醇、丝氨酸、甘氨酸、谷氨酸、丙氨酸、精氨酸、苏氨酸、脯氨酸、赖氨酸、亮氨酸、异亮氨酸、组氨酸\\\\n\\\\n### 3. 功效宣称\\\\n1. **专为油皮定制黑松露配方**：专为油性和混合肌调配配方，添加黑松露成分和保湿成分，平衡油脂分泌\\\\n2. **温和洁净**：氨基酸表活，温和清洁肌肤毛孔油脂和日常污垢，洗后不紧绷\\\\n3. **水润滋养保湿**：添加多重保湿成分，补充肌肤水分，洗后水润不干燥\\\\n\\\\n### 4. 产品规格信息\\\\n- 产品编号：CL0142\\\\n- 产品条码：697353769 128 4\\\\n- 色号：FC606Q\\\\n- 包装规格：大瓶 100g+小瓶 30g（旅行装小样），礼盒装\\\\n\\\\n### 5. 产品备案信息\\\\n- 备案人/生产企业：广东泰华医疗科技有限公司\\\\n- 企业地址：广东省汕头市潮南区峡山街道东山路东侧泰华工业园\\\\n- 化妆品生产许可证号：粤妆 20210003\\\\n- 产品批准文号：粤 G 妆网备字 2025372997\\\\n- 执行标准号：GB/T 29680（洗面奶型）\\\\n- 产地：广东省汕头市\\\\n- 备注：CULOFE 为注册商标，产品实际名称为酷洛菲\\\\n\\\\n### 6. 使用说明\\\\n**使用方法**: 取适量产品于掌心揉出泡沫，以打圈方式按摩面部，再用清水冲洗干净即可。\\\\n**注意事项**: 请置于阴凉干燥处，避免阳光直射；请置于儿童无法触及处；如有不适，请停止使用；请参见包装上的使用期限和产品提示。\\\",\\\"是否通过审核\\\":\\\"是\\\",\\\"问题列表\\\":[]}\"}",
  "debug_url": "https://www.coze.cn/work_flow?execute_id=7620373793232535606&space_id=7571647240440643626&workflow_id=7619646208533250090&execute_mode=2",
  "usage": {
    "token_count": 8575,
    "output_count": 3555,
    "input_count": 5020
  },
  "execute_id": "7620373793232535606"
}

print('=' * 60)
print('🎉 扣子工作流输出结果')
print('=' * 60)

# 解析嵌套 JSON
data = json.loads(api_response['data'])
sellpoints = json.loads(data['sellpoints'])

# 输出检查结果分析
print('\n📋 检查结果分析:\n')
print(sellpoints['检查结果分析'])

# 输出审核结果
print('\n\n✅ 审核结果:')
print(f"   是否通过：{sellpoints['是否通过审核']}")
print(f"   问题数量：{len(sellpoints['问题列表'])}")

# 输出执行信息
print('\n\n📊 执行信息:')
print(f"   执行 ID: {api_response['execute_id']}")
print(f"   Token 消耗：{api_response['usage']['token_count']}")
print(f"   输入 Token: {api_response['usage']['input_count']}")
print(f"   输出 Token: {api_response['usage']['output_count']}")
print(f"\n   🔗 调试链接:\n   {api_response['debug_url']}")

print('\n' + '=' * 60)
