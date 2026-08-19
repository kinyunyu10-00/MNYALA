/* =========================================================
   MNYALA ADMIN GLOBAL SEARCH
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const searchInput = document.getElementById("globalSearch");
    const clearButton = document.getElementById("clearSearch");

    if (!searchInput) {
        return;
    }


    /* =====================================================
       SEARCH
    ===================================================== */

    searchInput.addEventListener("input", () => {

        const searchTerm =
            searchInput.value.trim().toLowerCase();


        /* Show / hide clear button */

        if (clearButton) {

            clearButton.style.display =
                searchTerm.length > 0
                    ? "flex"
                    : "none";
        }


        /* Find searchable elements */

        const searchableItems =
            document.querySelectorAll(
                "[data-search]"
            );


        searchableItems.forEach(item => {

            const text =
                item
                    .getAttribute("data-search")
                    .toLowerCase();


            if (
                searchTerm === "" ||
                text.includes(searchTerm)
            ) {

                item.style.display = "";

            } else {

                item.style.display = "none";

            }

        });

    });


    /* =====================================================
       CLEAR SEARCH
    ===================================================== */

    if (clearButton) {

        clearButton.addEventListener("click", () => {

            searchInput.value = "";

            clearButton.style.display = "none";

            searchInput.focus();


            /* Show everything again */

            const searchableItems =
                document.querySelectorAll(
                    "[data-search]"
                );


            searchableItems.forEach(item => {

                item.style.display = "";

            });

        });

    }


    /* =====================================================
       ESC KEY
    ===================================================== */

    searchInput.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {

            searchInput.value = "";

            if (clearButton) {
                clearButton.style.display = "none";
            }


            const searchableItems =
                document.querySelectorAll(
                    "[data-search]"
                );


            searchableItems.forEach(item => {

                item.style.display = "";

            });

        }

    });

});