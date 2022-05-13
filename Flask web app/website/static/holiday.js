holidaytID = null;

function deleteHolidayt(holidayId) {
    holidayID = holidayId;
    jQuery('#delete-modal').modal({show:true});
}

document.addEventListener('DOMContentLoaded', function(){
      jQuery('#yes-btn').click(function() {
        fetch("/delete-holiday", {
          method: "POST",
          body: JSON.stringify({ holidayId: holidayID }),
        }).then((_res) => {
          window.location.href = "/home";
        });
      });
});