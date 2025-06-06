document.addEventListener("DOMContentLoaded", function () {
  if (window.fromCheckPage) {
    document.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        const nextForm = document.getElementById("nextForm");
        if (nextForm) {
          nextForm.submit();
        }
      }
    });
  }
});

console.log("main.js loaded");


function searchWord() {
    const keyword = document.getElementById("searchInput").value.trim();
    const resultBox = document.getElementById("searchResult");
    resultBox.innerHTML = "🔍 검색 중...";

    fetch("/search_word", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword: keyword })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            resultBox.innerHTML = `<p style="color:red;">${data.error}</p>`;
            return;
        }

        if (data.results.length === 0) {
            resultBox.innerHTML = "<p>❗ 일치하는 단어가 없습니다.</p>";
            return;
        }

        resultBox.innerHTML = data.results.map(item => `
            <div class="answer-box">
                <strong>단어:</strong> ${item.word}<br>
                <strong>뜻:</strong> ${item.definition}<br>
                ${item.example ? `<strong>예문:</strong> <em>${item.example}</em>` : ""}
            </div>
        `).join("");
    })
    .catch(err => {
        resultBox.innerHTML = "<p style='color:red;'>오류가 발생했습니다.</p>";
        console.error(err);
    });
}