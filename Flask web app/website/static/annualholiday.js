annualHolidayID = null;

function deleteHoliday(annualHolidayId) {
  annualHolidayID = annualHolidayId;
  jQuery('#delete-modal').modal({show:true});
}

document.addEventListener('DOMContentLoaded', function(){
      jQuery('#yes-btn').click(function() {
        fetch("/delete-annualholiday", {
          method: "POST",
          body: JSON.stringify({ annualHolidayId: annualHolidayID }),
        }).then((_res) => {
          window.location.href = "/annualholiday";
        });
      });
});
