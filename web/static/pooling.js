function check_notifications(){
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if(xhr.readyState == 4 && xhr.status == 200){
            console.info(xhr.responseText);
            alert("zmienił się status paczki: "+xhr.responseText)
            setTimeout(check_notifications, 1000); // powtórka kiedy nie uda się odebrać wiado
        }
    };
    xhr.open("GET", '/notifications', true);
    xhr.timeout = 15000;
    xhr.ontimeout = function () {
        console.error("Timeout");
        setTimeout(check_notifications, 1000);
    };
    xhr.send();
}
check_notifications()