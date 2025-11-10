(function () {
  function getCookie(name) {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2)
      return parts.pop().split(';').shift()
  }

  const theme = getCookie('theme') || 'system'
  let themeToApply = theme

  if (theme === 'system') {
    themeToApply = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  if (themeToApply === 'dark') {
    document.documentElement.classList.add('app-dark')
  }
})()
