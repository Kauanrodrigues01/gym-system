(() => {
    const buttonCloseMenu = document.querySelector('.button-close-menu');
    const buttonShowMenu = document.querySelector('.button-show-menu');
    const menuContainer = document.querySelector('.menu-container');
  
    const buttonShowMenuVisibleClass = 'button-show-menu-visible';
    const menuHiddenClass = 'menu-hidden';
  
    const closeMenu = () => {
      buttonShowMenu.classList.add(buttonShowMenuVisibleClass);
      menuContainer.classList.add(menuHiddenClass);
    };
  
    const showMenu = () => {
      buttonShowMenu.classList.remove(buttonShowMenuVisibleClass);
      menuContainer.classList.remove(menuHiddenClass);
    };
  
    // Adiciona ouvintes de evento para abrir e fechar o menu
    if (buttonCloseMenu) {
      buttonCloseMenu.addEventListener('click', closeMenu);
    }
  
    if (buttonShowMenu) {
      buttonShowMenu.addEventListener('click', showMenu);
    }
  })();
  