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
        iconPath: 'assets/tabbar/tab-home.png',
        selectedIconPath: 'assets/tabbar/tab-home-active.png',
        text: '首页',
      },
      {
        pagePath: 'pages/messages/index',
        iconPath: 'assets/tabbar/tab-messages.png',
        selectedIconPath: 'assets/tabbar/tab-messages-active.png',
        text: '消息',
      },
      {
        pagePath: 'pages/profile/index',
        iconPath: 'assets/tabbar/tab-profile.png',
        selectedIconPath: 'assets/tabbar/tab-profile-active.png',
        text: '我的',
      },
    ],
  },
})
