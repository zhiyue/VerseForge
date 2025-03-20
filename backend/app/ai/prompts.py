"""
小说生成相关的提示模板
"""

# 故事大纲生成
OUTLINE_PROMPT = """
请为一部{genre}小说创建详细的故事大纲。目标字数为{target_words}字。

要求：
1. 创建引人入胜的故事情节
2. 设计合理的故事结构（起承转合）
3. 安排适当的情节转折点
4. 确保故事的完整性和连贯性

请以JSON格式返回，包含以下内容：
1. 故事简介
2. 主要情节线
3. 次要情节线
4. 关键转折点
5. 章节规划
"""

# 人物创建
CHARACTER_PROMPT = """
请为{genre}小说创建一个{role_type}角色。

要求：
1. 创建鲜明的性格特征
2. 设计合理的背景故事
3. 定义个人动机和目标
4. 设置性格缺陷或内心矛盾

请以JSON格式返回，包含以下内容：
1. 基本信息（姓名、年龄等）
2. 性格特征
3. 背景故事
4. 动机和目标
5. 与其他角色的关系
"""

# 场景生成
SCENE_PROMPT = """
请为以下场景创建详细的描写：

场景背景：
{scene_context}

要求：
1. 生动的环境描写
2. 细致的氛围营造
3. 人物互动的自然流畅
4. 情感表达的恰到好处

涉及人物：
{characters}

情节要求：
{plot_requirements}
"""

# 对话生成
DIALOGUE_PROMPT = """
请为以下角色创建对话：

角色A：{character_a}
角色B：{character_b}

场景背景：
{scene_context}

情感基调：
{emotional_tone}

对话目的：
{dialogue_purpose}

要求：
1. 对话要符合角色性格
2. 体现人物关系
3. 推动情节发展
4. 表达自然流畅
"""

# 内容润色
POLISH_PROMPT = """
请对以下内容进行润色：

原文：
{content}

润色要求：
1. 提升文学性
2. 增强表现力
3. 保持原意
4. 风格统一

重点关注：
{focus_areas}
"""

# 情节连贯性检查
COHERENCE_PROMPT = """
请检查以下内容的连贯性：

前文概要：
{previous_content}

当前内容：
{current_content}

检查要点：
1. 情节连贯性
2. 人物表现一致性
3. 时间线合理性
4. 设定符合性

请以JSON格式返回检查结果，包含：
1. 是否连贯
2. 具体问题
3. 修改建议
"""

# 风格调整
STYLE_PROMPT = """
请将以下内容调整为{target_style}风格：

原文：
{content}

风格要求：
{style_requirements}

注意事项：
1. 保持原有情节
2. 调整表达方式
3. 突出风格特点
4. 保持连贯性
"""

# 情感渲染
EMOTION_PROMPT = """
请为以下场景增加情感渲染：

场景内容：
{scene_content}

情感基调：
{emotional_tone}

要求：
1. 细腻的情感描写
2. 恰当的氛围营造
3. 合理的情感递进
4. 打动人心的细节
"""

# 冲突升级
CONFLICT_PROMPT = """
请为以下冲突场景设计升级：

当前冲突：
{current_conflict}

涉及人物：
{involved_characters}

要求：
1. 合理的冲突升级
2. 扣人心弦的发展
3. 符合人物性格
4. 为后续情节埋伏笔
"""

# 高潮设计
CLIMAX_PROMPT = """
请为故事设计高潮部分：

前文概要：
{story_summary}

已建立的伏笔：
{previous_hints}

要求：
1. 扣人心弦的展开
2. 合理的伏笔回收
3. 出人意料的转折
4. 令人满意的解决
"""

# 结局设计
ENDING_PROMPT = """
请为故事设计结局：

故事概要：
{story_summary}

主要人物归宿：
{character_fates}

要求：
1. 合理的情节收束
2. 完整的人物归宿
3. 留下余味和思考
4. 符合故事主题
"""