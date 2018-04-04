const translationSwitcher = document.querySelector('.translation-switcher'),
  articleSwitcher = document.querySelector('.article-switcher'),
  articleList = document.querySelector('.article-list'),
  translationList = document.querySelector('.translation-list')

translationSwitcher.addEventListener('click', () => {
  translationSwitcher.classList.add('active')
  articleSwitcher.classList.remove('active')
  /*articleList.style.opacity = 0*/
  fadeOut(articleList)
  fadeIn(translationList)
})
articleSwitcher.addEventListener('click', () => {
  translationSwitcher.classList.remove('active')
  articleSwitcher.classList.add('active')
  /*translationList.style.opacity = 0*/
  fadeOut(translationList)
  fadeIn(articleList)
})

/* http://youmightnotneedjquery.com/ */
function fadeIn(element) {
  element.style.opacity = 0
  var last = +new Date()
  var tick = function() {
    element.style.opacity = +element.style.opacity + (new Date() - last) / 400
    last = +new Date()
    if (+element.style.opacity < 1) {
      ;(window.requestAnimationFrame && requestAnimationFrame(tick)) ||
        setTimeout(tick, 16)
    }
  }
  tick()
}
function fadeOut(element) {
  element.style.opacity = 1
  var last = +new Date()
  var tick = function() {
    element.style.opacity = +element.style.opacity - (new Date() - last) / 400
    last = +new Date()
    if (+element.style.opacity > 0) {
      ;(window.requestAnimationFrame && requestAnimationFrame(tick)) ||
        setTimeout(tick, 16)
    }
  }
  tick()
}
