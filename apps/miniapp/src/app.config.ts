export default defineAppConfig({
  pages: [
    'pages/home/index',
    'pages/questionnaire/index',
    'pages/questionnaire-result/index',
    'pages/screening/index',
    'pages/service-request/index',
    'pages/share-card/index',
    'pages/messages/index',
    'pages/chat/index',
    'pages/profile/index',
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff8ed',
    navigationBarTitleText: '河狸数字能源',
    navigationBarTextStyle: 'black',
  },
  tabBar: {
    color: '#b3a08a',
    selectedColor: '#ff7a00',
    backgroundColor: '#fffaf3',
    borderStyle: 'white',
    list: [
      {
        pagePath: 'pages/home/index',
        text: '首页',
      },
      {
        pagePath: 'pages/messages/index',
        text: '消息',
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的',
      },
    ],
  },
})
