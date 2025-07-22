try {
  while (true) {
    document.querySelector("li[role=button]").click()
  }
} catch {
}

const nodes = [...document.querySelectorAll("li>div>div.AeY9P")]

let result = 'vietnamese,english'
for (node of nodes) {
  if (!node.childNodes) continue
  const vietnamese = node.childNodes[1].childNodes[0].innerText
  const english = node.childNodes[1].childNodes[1].innerText
  result += `\n"${vietnamese}","${english}"`
}
result += '\n'

async function sleep(ms) {
  await new Promise((resolve, _) => {
    setTimeout(() => resolve, ms)
  })
}

async function go() {
  for (node of nodes) {
    if (!node.childNodes) continue
    node.childNodes[0].childNodes[0].click()
    await sleep(2_000)
  }
}
go().catch(e => console.log(e))

result
