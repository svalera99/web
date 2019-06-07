let data = [];
fetch("static/js/posts.json").then(res => res.json()).then(list => {
    for (j = 1; j <= Object.keys(list).length; ++j) {
        data.push(Object.values(list[j]));
    }
    var div = document.getElementById("articles_div");
    for (k = 0; k < data.length; ++k) {
        var artc = document.createElement("article");
        artc.id = k;
        div.appendChild(artc);
        let x = {
            picture: data[k][0],
            name: data[k][1],
            illness: data[k][2],
            status: data[k][3],
            age: data[k][4],
            blood_type: data[k][5],
            where: data[k][6]
        };
        $("#" + k.toString()).loadTemplate($("#template"), x);
    }
});
