window.onload = function () {
    let path = window.location.pathname;
    let page = path.split("/").pop();
    console.log(1);
    let botom_page_list = ["login.html", "register.html", "make_post.html", "header.html"];
    if (botom_page_list.indexOf(page) > -1){
        let footer = document.getElementsByClassName("footer");
        footer[0].style.position = 'absolute';
        footer[0].style.bottom = '0';
    };
};