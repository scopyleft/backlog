/* Preloader fadeout when page is loaded */
var preloader = document.querySelector('#preloader')
preloader.classList.add('fadeout')
setTimeout(() => {
    preloader.classList.add('hidden')
}, 300)

/* open menu */
Array.from(document.querySelectorAll('button.menu')).forEach(button => {
    button.addEventListener('click', () => {
    const activeButton = document.querySelector('button.active.menu')
        if (activeButton) {
            activeButton.classList.remove('active')
            if (activeButton !== button) {
                button.classList.add('active')
            }
        } else {
            button.classList.add('active')
        }
    })
})

/* external link in new tab */
Array.from(document.querySelectorAll('a')).forEach(a => {
    if (a.href.search(/\w+:\/\//) === 0 && a.hostname !== location.hostname) a.setAttribute('target', '_blank')
})

/* animation flash info */
const flashes = document.querySelector('.flashes')
if (flashes) {
    setTimeout(() => {
        flashes.classList.add('hidden')
    }, 3000)
}

/* display profile social network field on click */
const socialIcons = Array.from(document.querySelectorAll('.social-networks li'))
if (socialIcons) {
    socialIcons.forEach(socialIcon => {
        socialIcon.querySelector('a').addEventListener('click', (event) => {
            event.preventDefault()
            const SocialsClick = socialIcon.querySelector('a').contains(event.target)
            if (SocialsClick) {
                socialIcons.forEach((li) => li.classList.remove('active'))
                socialIcon.classList.add('active')
                socialIcon.querySelector('input').focus()
            } else {
                socialIcon.classList.remove('active')
            }
        })
    })
}

function activateInput(input) {
  const parent = input.parentElement
  parent.classList.add('active', 'completed')
}
function deactivateInput(input) {
  const parent = input.parentElement
  parent.classList.remove('active', 'completed')
}

/* Detect chrome autofill https://stackoverflow.com/questions/35049555/chrome-autofill-autocomplete-no-value-for-password/38269071 comm ben */
const autofillContent = `"${String.fromCharCode(0xFEFF)}"`
function checkAutofill(input) {
  if (!input.value) {
    const style = window.getComputedStyle(input)
    if (style.content !== autofillContent)
      return false
  }
  activateInput(input)
  return true
}
const input = document.querySelector('input[type=password]')
if (!checkAutofill(input)) {
  deactivateInput(input)
  let interval = 0
  const intervalId = setInterval(() => {
    if (checkAutofill(input) || interval++ >= 20){
      activateInput(input)
      clearInterval(intervalId)
    }
  }, 100)
}
/* animation login fields */
Array.from(document.querySelectorAll('.authentication-form > div > input')).forEach(input => {
    if (input.value) {
        activateInput(input)
    }
    input.addEventListener('change', () => {
        activateInput(input)
    })
    input.addEventListener('focus', () => {
        activateInput(input)
    })
    input.addEventListener('blur', () => {
        if (input.value) return
        deactivateInput(input)
    })
})

/* animation title field create article */
Array.from(document.querySelectorAll('h1.edit input')).forEach(inputh1 => {
    const h1 = inputh1.parentElement
    inputh1.addEventListener('focus', () => {
        h1.classList.add('active')
    })
    inputh1.addEventListener('blur', () => {
        if (inputh1.value) return
        h1.classList.remove('active')
    })
})

/* highlight file upload area on hover or dragenter */
function addListenerMulti(element, events, fn) {
    events.split(' ').forEach(event => element.addEventListener(event, fn, false)) /* https://stackoverflow.com/questions/8796988/binding-multiple-events-to-a-listener-without-jquery */
}
const fileInput = document.querySelector('.file input')
const dropArea = document.querySelector('canvas')
if (fileInput) {
    addListenerMulti(fileInput, 'dragenter focus click', () => {
        dropArea.classList.add('active')
    })
    addListenerMulti(fileInput, 'dragleave blur drop', () => {
        dropArea.classList.remove('active')
    })
    fileInput.addEventListener('change', () => {
        document.querySelector('.file label').innerHTML(' ')
    })
}
