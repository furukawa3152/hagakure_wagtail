window.addEventListener('DOMContentLoaded', () => {
  const body = document.body; // bodyを対象にする

  const createSnow = () => {
    const snowEl = document.createElement('span');
    snowEl.className = 'snow';
    const minSize = 5;
    const maxSize = 10;
    const size = Math.random() * (maxSize - minSize) + minSize;
    snowEl.style.width = `${size}px`;
    snowEl.style.height = `${size}px`;
    snowEl.style.left = Math.random() * window.innerWidth + 'px'; // windowの幅を基準に
    body.appendChild(snowEl); // bodyに雪を追加

    setTimeout(() => {
      snowEl.remove();
    }, 20000);
  }

  setInterval(createSnow, 100);
});
