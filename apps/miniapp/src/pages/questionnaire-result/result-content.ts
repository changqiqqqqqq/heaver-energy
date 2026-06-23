export type ResultTheme = 'flame' | 'drip' | 'growth' | 'shield' | 'bolt' | 'scale'

export type ResultSignal = {
  prefix: string
  highlight: string
  suffix?: string
  icon: string
}

export type ResultAction = {
  type: 'report' | 'consult'
  icon: string
  title: string
  subtitle: string
}

export type ResultContent = {
  theme: ResultTheme
  icon: string
  title: string
  subtitle: string
  stat: string
  statLabel: string
  signals: ResultSignal[]
  warning: string
  nextActions: ResultAction[]
  footerNote: string
}

// 六类结果页按设计稿固定映射，避免后端文案缺失时破坏视觉一致性。
export const resultContentByProfile: Record<string, ResultContent> = {
  cost_sensitive: {
    theme: 'flame',
    icon: '火',
    title: '成本敏感型',
    subtitle: '每分钱都要花得明白',
    stat: '8–18%',
    statLabel: '同类企业电费平均可优化空间',
    signals: [
      { prefix: '固定支出压力大，但电费', highlight: '从没系统测算过', icon: '算' },
      { prefix: '没有同行对比，不知道', highlight: '贵在哪、能不能省', icon: '人' },
      { prefix: '利润被压薄，但具体被谁压薄', highlight: '说不清', icon: '查' },
    ],
    warning: '不主动查，这笔钱会一直悄悄流走',
    nextActions: [
      { type: 'report', icon: '告', title: '领取专属电费优化报告', subtitle: '查看我的降本建议 · 免费' },
      { type: 'consult', icon: '顾', title: '让顾问帮我看一看', subtitle: '10分钟初步判断 · 免费' },
    ],
    footerNote: '数据为同类企业经验参考，实际优化空间需结合账单进一步判断。',
  },
  hidden_waste: {
    theme: 'drip',
    icon: '滴',
    title: '隐性浪费型',
    subtitle: '钱在漏，但你不知道从哪漏',
    stat: '3个',
    statLabel: '同类企业平均发现的隐性漏钱点',
    signals: [
      { prefix: '每月钱去了哪里，', highlight: '说不清', suffix: '就是一个信号', icon: '查' },
      { prefix: '供应商很少比较，可能有人在', highlight: '安静多收钱', icon: '人' },
      { prefix: '电费账单是入口，但你可能', highlight: '从没认真看过', icon: '算' },
    ],
    warning: '先找到最可能漏钱的位置，再决定要不要深入查',
    nextActions: [
      { type: 'report', icon: '告', title: '领取漏钱点排查报告', subtitle: '查看我的诊断结果 · 免费' },
      { type: 'consult', icon: '顾', title: '让顾问帮我梳理漏点', subtitle: '15分钟找出优先排查项 · 免费' },
    ],
    footerNote: '数据为同类企业经验参考，实际问题需结合账单、报价和合同进一步判断。',
  },
  growth_expansion: {
    theme: 'growth',
    icon: '↗',
    title: '增长扩张型',
    subtitle: '业务在涨，成本结构没跟上',
    stat: '2–3倍',
    statLabel: '扩张期企业成本超支风险',
    signals: [
      { prefix: '采购和用能支出同步放大，但可能', highlight: '没人系统管', icon: '图' },
      { prefix: '新场地/新设备合同，往往决定', highlight: '未来电费高低', icon: '电' },
      { prefix: '现在多花的冤枉钱，会随着规模', highlight: '持续叠加', icon: '升' },
    ],
    warning: '扩张时做一次把关，比日后返工省得多',
    nextActions: [
      { type: 'report', icon: '告', title: '领取扩张期成本体检报告', subtitle: '查看扩张期降本建议 · 免费' },
      { type: 'consult', icon: '顾', title: '让顾问帮我做把关', subtitle: '用能与供应商初筛 · 免费' },
    ],
    footerNote: '数据为行业经验参考，实际风险需结合企业扩张节奏、用能规模和合同安排判断。',
  },
  stable_operation: {
    theme: 'shield',
    icon: '盾',
    title: '稳健经营型',
    subtitle: '现在不是最坏，但可能不是最好',
    stat: '60%+',
    statLabel: '稳定期企业存在“习惯性多付”',
    signals: [
      { prefix: '供应商多年没换过，但可能', highlight: '从没主动比较过', icon: '人' },
      { prefix: '电费合同签完就放着，', highlight: '很少回头复核', icon: '算' },
      { prefix: '成本结构清晰，但清晰', highlight: '不等于最优', icon: '盾' },
    ],
    warning: '低干扰体检，能帮你确认是否还有优化空间',
    nextActions: [
      { type: 'report', icon: '告', title: '领取经营体检报告', subtitle: '看看是否还有优化空间 · 免费' },
      { type: 'consult', icon: '顾', title: '让顾问做低干扰初筛', subtitle: '不影响经营，先看大方向 · 免费' },
    ],
    footerNote: '数据为同类企业经验参考，实际优化空间需结合账单和现有服务合同判断。',
  },
  energy_awakened: {
    theme: 'bolt',
    icon: '电',
    title: '能源觉醒型',
    subtitle: '电费这件事，你可能一直在多交',
    stat: '10–25%',
    statLabel: '工商业用户电费可优化常见区间',
    signals: [
      { prefix: '电费支出不低，但从来没人', highlight: '系统分析过', icon: '电' },
      { prefix: '售电、光伏、储能都听过，但不知道', highlight: '哪个适合', icon: '图' },
      { prefix: '电费账单细节多，自己看', highlight: '很难看出空间', icon: '查' },
    ],
    warning: '不确认是否合理，每个月都在重复多付',
    nextActions: [
      { type: 'report', icon: '告', title: '领取专属电费优化报告', subtitle: '判断有没有节省空间 · 免费' },
      { type: 'consult', icon: '顾', title: '让顾问帮我看账单', subtitle: '账单初筛与方案判断 · 免费' },
    ],
    footerNote: '数据为行业经验参考，实际优化空间需结合用电量、峰谷结构、合同方式等判断。',
  },
  supplier_confused: {
    theme: 'scale',
    icon: '秤',
    title: '供应商困惑型',
    subtitle: '报价拿到手，却看不出值不值',
    stat: '70%+',
    statLabel: '中小企业从未主动复核供应商报价',
    signals: [
      { prefix: '主要靠熟人介绍，信息差可能让你', highlight: '持续多付', icon: '人' },
      { prefix: '收到报价单，却看不懂', highlight: '好不好、贵不贵', icon: '算' },
      { prefix: '合同服务边界模糊，往往是', highlight: '扯皮和超支根源', icon: '秤' },
    ],
    warning: '不复核，信息差会一直存在',
    nextActions: [
      { type: 'report', icon: '告', title: '领取供应商报价复核清单', subtitle: '判断报价是否值得签 · 免费' },
      { type: 'consult', icon: '顾', title: '让顾问帮我看报价', subtitle: '报价/合同/方案初步判断 · 免费' },
    ],
    footerNote: '数据为行业调研参考，实际情况需结合报价单、合同和交付范围判断。',
  },
}

export const getResultContent = (profileCode?: string | null) => {
  return resultContentByProfile[profileCode || ''] || resultContentByProfile.energy_awakened
}
