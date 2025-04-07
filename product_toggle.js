var li_elements = document.querySelectorAll(".product_slider .product_slider_div li");
var item_elements = document.querySelectorAll(".companies");
for (var i = 0; i < li_elements.length; i++) {
  li_elements[i].addEventListener("click", function() {
    li_elements.forEach(function(li) {
      li.classList.remove("activep");
    });
    this.classList.add("activep");
    var li_value = this.getAttribute("data-li");
    item_elements.forEach(function(item) {
      item.style.display = "none";
    });
    if (li_value == "amazon") {
      document.querySelector("." + li_value).style.display = "block";
    } else if (li_value == "flipkart") {
      document.querySelector("." + li_value).style.display = "block";
    } else if (li_value == "snapdeal") {
      document.querySelector("." + li_value).style.display = "block";
    } else if (li_value == "slatehouse") {
      document.querySelector("." + li_value).style.display = "block";
    }else if (li_value == "tata") {
      document.querySelector("." + li_value).style.display = "block";
    }else if (li_value == "myntra") {
      document.querySelector("." + li_value).style.display = "block";
    }else if (li_value == "ajio") {
      document.querySelector("." + li_value).style.display = "block";
    }else if (li_value == "random") {
      document.querySelector("." + li_value).style.display = "block";
    }else {
      console.log("");
    }
  });
}
