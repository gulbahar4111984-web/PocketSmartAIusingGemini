function money(
    value,
    currency
) {
    try {
        return new Intl.NumberFormat(
            undefined,
            {
                style: "currency",
                currency: currency || "INR",
                maximumFractionDigits: 0
            }
        ).format(value);

    } catch {
        return `${currency || "INR"} ${value}`;
    }
}


function escapeHtml(value) {

    return String(
        value ?? ""
    ).replace(
        /[&<>'"]/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "'": "&#39;",
            '"': "&quot;"
        })[character]
    );
}


function showResult(result) {

    const element =
        document.getElementById(
            "result"
        );

    const items = result.items || [];

    const tips = result.tips || [];

    element.innerHTML = `
        <div class="card">

            <div class="recommendation-head">

                <div>

                    <p class="eyebrow">
                        ${escapeHtml(
                            result.planner_type
                                .toUpperCase()
                        )}
                        PLAN ·
                        ${escapeHtml(
                            result.source
                        )}
                    </p>

                    <h2>
                        ${escapeHtml(
                            result.title
                        )}
                    </h2>

                    <p>
                        ${escapeHtml(
                            result.summary
                        )}
                    </p>

                </div>

                <div>

                    <div class="metric">
                        ${money(
                            result.estimated_total,
                            result.currency
                        )}
                    </div>

                    <small>
                        estimated total
                    </small>

                </div>

            </div>

            <p>
                <strong>Budget:</strong>
                ${money(
                    result.total_budget,
                    result.currency
                )}

                ·

                <strong>Remaining:</strong>
                ${money(
                    result.remaining_budget,
                    result.currency
                )}
            </p>

            <div class="item-grid">

                ${items.map(item => `
                    <article class="item">

                        <h3>
                            ${escapeHtml(
                                item.name
                            )}
                        </h3>

                        <div class="price">
                            ${money(
                                item.estimated_price,
                                item.currency
                            )}
                        </div>

                        <small>
                            ${escapeHtml(
                                item.category
                            )}
                            ·
                            ${escapeHtml(
                                item.provider
                            )}
                        </small>

                        <p>
                            ${escapeHtml(
                                item.why_it_fits
                            )}
                        </p>

                        <a
                            href="${escapeHtml(
                                item.search_url
                            )}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Search on
                            ${escapeHtml(
                                item.provider
                            )}
                            ↗
                        </a>

                    </article>
                `).join("")}

            </div>

            <h3>
                Tips
            </h3>

            <ul>
                ${tips.map(tip => `
                    <li>
                        ${escapeHtml(tip)}
                    </li>
                `).join("")}
            </ul>

            <small>
                ${escapeHtml(
                    result.disclaimer
                )}
            </small>

        </div>
    `;

    element.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


async function submitPlanner(
    formId,
    url,
    multipart = false
) {

    const form =
        document.getElementById(
            formId
        );

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const button =
                form.querySelector(
                    "button"
                );

            const originalText =
                button.textContent;

            button.disabled = true;
            button.textContent =
                "Generating...";

            try {

                let options;

                if (multipart) {

                    options = {
                        method: "POST",
                        body: new FormData(
                            form
                        )
                    };

                } else {

                    options = {
                        method: "POST",
                        body: JSON.stringify(
                            formObject(form)
                        )
                    };
                }

                const result =
                    await api(
                        url,
                        options
                    );

                showResult(result);

                await loadHistory();

            } catch (error) {

                document.getElementById(
                    "result"
                ).innerHTML = `
                    <div class="card error">
                        ${escapeHtml(
                            error.message
                        )}
                    </div>
                `;

            } finally {

                button.disabled = false;
                button.textContent =
                    originalText;
            }
        }
    );
}


async function loadHistory() {

    const element =
        document.getElementById(
            "history"
        );

    if (!element) {
        return;
    }

    try {

        const rows =
            await api(
                "/api/history"
            );

        if (!rows.length) {

            element.innerHTML =
                "<p>No recommendations yet.</p>";

            return;
        }

        element.innerHTML =
            rows.map(row => `

                <div class="history-row">

                    <div>

                        <strong>
                            ${escapeHtml(
                                row.planner_type
                            )}
                        </strong>

                        <div>
                            ${escapeHtml(
                                row.response.title
                            )}
                        </div>

                    </div>

                    <small>
                        ${new Date(
                            row.created_at
                        ).toLocaleString()}
                    </small>

                </div>

            `).join("");

    } catch (error) {

        element.innerHTML = `
            <p class="error">
                ${escapeHtml(
                    error.message
                )}
            </p>
        `;
    }
}


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        try {

            const session =
                await api(
                    "/api/auth/session-info"
                );

            const welcome =
                document.getElementById(
                    "welcome"
                );

            const status =
                document.getElementById(
                    "sessionStatus"
                );

            if (welcome) {
                welcome.textContent =
                    `Hello, ${session.full_name}`;
            }

            if (status) {
                status.textContent =
                    "Signed in";
            }

        } catch {

            window.location.href =
                "/login";

            return;
        }


        document
            .querySelectorAll(".tab")
            .forEach(tab => {

                tab.addEventListener(
                    "click",
                    () => {

                        document
                            .querySelectorAll(
                                ".tab"
                            )
                            .forEach(item =>
                                item.classList.remove(
                                    "active"
                                )
                            );

                        document
                            .querySelectorAll(
                                ".planner-panel"
                            )
                            .forEach(panel =>
                                panel.classList.remove(
                                    "active"
                                )
                            );

                        tab.classList.add(
                            "active"
                        );

                        const panel =
                            document.getElementById(
                                tab.dataset.tab
                            );

                        panel?.classList.add(
                            "active"
                        );
                    }
                );
            });


        submitPlanner(
            "homeForm",
            "/api/planners/home"
        );

        submitPlanner(
            "partyForm",
            "/api/planners/party"
        );

        submitPlanner(
            "jewelryForm",
            "/api/planners/jewelry",
            true
        );

        loadHistory();
    }
);