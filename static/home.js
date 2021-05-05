window.onload=function(){
    input = document.getElementById("search-input");
    searchBtn = document.getElementById("search-btn");


const expand = () => {
  searchBtn.classList.toggle("close");
  input.classList.toggle("square");
};

searchBtn.addEventListener("click", expand);

}
