const tabsBoxp = document.querySelector(".product_slider_div"),
allTabsp = tabsBoxp.querySelectorAll(".sli_tab"),
arrowIconsp = document.querySelectorAll(".iconp i");
let isDraggingp = false;
const handleIconsp = (scrollVal) => {
    let maxScrollableWidth = tabsBoxp.scrollWidth - tabsBoxp.clientWidth;
    arrowIconsp[0].parentElement.style.display = scrollVal <= 0 ? "none" : "flex";
    arrowIconsp[1].parentElement.style.display = maxScrollableWidth - scrollVal <= 1 ? "none" : "flex";
}
arrowIconsp.forEach(icon => {
    icon.addEventListener("click", () => {
        // if clicked icon is left, reduce 350 from tabsBox scrollLeft else add
        let scrollWidth = tabsBoxp.scrollLeft += icon.id === "leftp" ? -340 : 340;
        handleIconsp(scrollWidth);
    });
});
allTabsp.forEach(tab => {
    tab.addEventListener("click", () => {
        tabsBoxp.querySelector(".activep").classList.remove("activep");
        tab.classList.add("activep");
    });
});

const draggingp = (e) => {
    if(!isDraggingp) return;
    tabsBoxp.classList.add("draggingp");
    tabsBoxp.scrollLeft -= e.movementX;
    handleIconsp(tabsBoxp.scrollLeft)
}
const dragStopp = () => {
    isDraggingp = false;
    tabsBoxp.classList.remove("draggingp");
}
tabsBoxp.addEventListener("mousedown", () => isDraggingp = true);
tabsBoxp.addEventListener("mousemove", draggingp);
document.addEventListener("mouseup", dragStopp);
