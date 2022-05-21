var height_controler = 0;

function open_side_menu(){
    let screen_size = screen.width;
    let side_menu = document.getElementById('side-menu');

    if (screen_size <= 600)
        side_menu.style.width = '100%';
    else
        side_menu.style.width = '500px'
}

function toggle_close(){
    let side_menu = document.getElementById('side-menu');
    side_menu.style.width = '0px'
}

function show_info(i){
    let list_item = document.getElementsByClassName('list-item');
    let item = document.getElementsByClassName('item');

    if (i > 0){
        list_item[i - 1].style.height = '0px';

    } else{
        for (let j = 0; j < list_item.length; j++){
            list_item[j].style.height = '0px'
            item[j].style.fontSize = '1em';
            item[item.length - j].style.fontSize = '1em';
        }
    }
    
    if (height_controler == 0){
        list_item[i].style.height = '150px';
        item[i+1].style.fontSize = '1.5em';
        height_controler = 1
    }else{
        list_item[i].style.height = '0px'
        item[i+1].style.fontSize = '1em';
        height_controler = 0
    }
}

function new_user_validator(){
    let passwd = document.getElementById('passwd').value
    let chk_passwd = document.getElementById('passwd1').value
    let chars = '~!@#$%^&*()_+}":>?<1234567890'

}

