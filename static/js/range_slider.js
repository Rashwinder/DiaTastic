let range=document.querySelector("input[type=range]");
let number=document.querySelector('input[type=number]')

range.addEventListener("input",(e)=>{
  number.value=e.target.value;
})
number.addEventListener("input",(e)=>{
  range.value=e.target.value;
})