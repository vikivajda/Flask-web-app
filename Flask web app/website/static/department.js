departmentID = null;

function deleteDepartment(departmentId) {
    departmentID = departmentId;
    jQuery('#delete-modal').modal({show:true});
}

document.addEventListener('DOMContentLoaded', function(){
      jQuery('#yes-btn').click(function() {
        fetch("/delete-department", {
          method: "POST",
          body: JSON.stringify({ departmentId: departmentID }),
        }).then((_res) => {
          window.location.href = "/department";
        });
      });
});