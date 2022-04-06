document.querySelectorAll('thead')
    .forEach(thead => {
        thead.addEventListener('click', function(event) {
          if (! event.target.matches('button')) { return; }
          event.target.classList.toggle('closed');
          const index = event.target.dataset.index;
          const selector = `tbody[data-index="${index}"]`;
          document.querySelector(selector).classList.toggle('closed');
        });
    });

//function toggleColors() {
//    for (let i = 0; i < 14; ++i) {
//        document.querySelectorAll(`.c${i}`).forEach(function (span) {
//            span.classList.toggle(`cc${i}`);
//        });
//        document.querySelectorAll(`.b${i}`).forEach(function (span) {
//            span.classList.toggle(`bb${i}`);
//        });
//    }
//}
//
//document.querySelectorAll('input[type=radio]').forEach(function(item) {
//    item.addEventListener('change', function(event) {
//        toggleColors();
//    });
//});


//document.querySelector('#by-part').checked = true;
