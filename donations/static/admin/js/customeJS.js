var modal = document.getElementById("myModal");

var modalImg = document.getElementById("img01");

$('.myImg').click(function() {
  modal.style.display = "block";
  modalImg.src = this.src;
});

$('.Imgclose').click(function() {
  modal.style.display = "none";
});
