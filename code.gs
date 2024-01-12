function omomi() {
  const discordWebHookURL = "webhook";

  // 投稿するチャット内容と設定
  const message = {
    "content": "重み確認しろ"
  }

  const param = {
    "method": "POST",
    "headers": { 'Content-type': "application/json" },
    "payload": JSON.stringify(message)
  }

  UrlFetchApp.fetch(discordWebHookURL, param);
}
