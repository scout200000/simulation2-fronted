export function mountVariantNav(current) {
  const nav = document.createElement("nav");
  nav.className = "frontend-variant-nav";
  nav.innerHTML = `
    <a href="./index.html">项目首页</a>
    <a href="./v1.html" class="${current === "v1" ? "active" : ""}">V1</a>
    <a href="./v2.html" class="${current === "v2" ? "active" : ""}">V2</a>
  `;
  document.body.appendChild(nav);
}
