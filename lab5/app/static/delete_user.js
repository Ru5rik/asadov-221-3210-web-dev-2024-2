"use strict"

function fillModal(event) {
    let deleteUrl = event.relatedTarget.dataset.deleteUrl;
    let name = event.relatedTarget.dataset.name;
    
    let title = event.target.querySelector(".modal-title");
    title.innerHTML = "Вы уверены, что хотите удалить пользователя " + name;
    
    let modalForm = event.target.querySelector("form");
    modalForm.action = deleteUrl;
}

window.onload = function () {
    let deleteModal = document.getElementById("delete-modal");
    deleteModal.addEventListener("show.bs.modal", fillModal);
}