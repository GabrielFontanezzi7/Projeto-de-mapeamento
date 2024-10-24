$(".menu > ul > li").click(function (e) {
        // tirando o active
    $(this).siblings().removeClass("active");
        // colar o active no clicado
    $(this).toggleClass("active");
        // Abrir sub-menu se tiver
    $(this).find("ul").slideToggle();
        // fehcar sub-menu se tiver
    $(this).siblings().find("ul").slideUp();
        // retirar classes ativeas de sub menu itens
    $(this).siblings(),find("ul").find("li").removeClass("active");
});

$(".menu-btn").click(function () {
    $(".sidebar").toggleClass("active")
})