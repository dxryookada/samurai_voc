document.addEventListener('DOMContentLoaded', function () {
    function setTodayDate() {
        var today = new Date();
        var yyyy = today.getFullYear();
        var mm = ("0" + (today.getMonth() + 1)).slice(-2);
        var dd = ("0" + today.getDate()).slice(-2);
        var formattedDate = yyyy + '-' + mm + '-' + dd;
        document.getElementById("work-day").value = formattedDate;
        console.log(formattedDate);
    }
    
    // 関数を呼び出して実行
    setTodayDate();
});

