document.documentElement.classList.add("has-script");

requestAnimationFrame(() => {
  document.body.classList.add("is-revealed");
});

const currentPath = window.location.pathname.replace(/\/+$/, "");
for (const link of document.querySelectorAll(".chapter-ledger a, .reading-index a")) {
  const linkPath = new URL(link.href, window.location.href).pathname.replace(/\/+$/, "");
  if (linkPath === currentPath) {
    link.setAttribute("aria-current", "page");
  }
}
