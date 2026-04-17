popupContents = {
    "historical_nav": {
        "key": "historical_nav_popup",
        "title": "Historical Fund NAV: Performance Since Inception",
        "button_title": "Learn More About Historical NAV",
        "content_dict": {
            "Overview of Historical NAV": (
                "This chart provides a long-term view of the fund's Net Asset Value (NAV), "
                "showcasing its performance since inception."
            ),"Key Metrics": (
                "- **Weighted Performance**: The cumulative return of the fund over the selected period, "
                "adjusted to account for the relative contributions of different asset classes.\n"
                "- **Gross Asset Value (GAV)**: The total value of the fund's assets before deducting liabilities, "
                "providing insight into the scale and growth potential of the portfolio.\n"
                "- **Annualized Volatility**: A measure of the fund's risk, calculated as the standard deviation of returns "
                "on an annualized basis. Lower volatility indicates more stable performance."
            ),
            "Why This Matters": (
                "Understanding historical NAV trends provides insights into the fund's long-term performance, "
                "stability, and growth potential."
            ),
            "Risk-Free Rate": (
                "The risk-free rate represents the theoretical return on an investment with no risk of financial loss. "
                "Typically, this is based on the yield of government bonds, such as U.S. Treasury bills, which are considered "
                "the safest investment. It serves as a benchmark for evaluating the performance of the fund.\n\n"
                "In this chart, the risk-free rate is plotted alongside the fund's NAV to help investors assess the fund's "
                "risk-adjusted returns. By comparing the fund's growth trajectory to the risk-free rate, you can:\n"
                "- Determine the excess return achieved by the fund (also called **alpha**).\n"
                "- Understand whether the fund is outperforming a 'safe' investment over time.\n"
                "- Gauge the justification for the level of risk taken by the fund relative to its return."
            ),

        },
    },
    "date_nav": {
        "key": "date_nav_popup",
        "title": "NAV Analysis: Custom Start Date",
        "button_title": "Learn More About Custom NAV Analysis",
        "content_dict": {
            "Overview": (
                "This chart allows you to analyze the fund's NAV starting from a specific date, "
                "with metrics calculated dynamically from that date until today."
            ),
            "Date Selection Rules": (
                "- The selected start date must be at least **7 days before today**.\n"
                "- If a date less than 7 days prior is chosen, it defaults to **7 days before today**."
            ),
            "What This Chart Displays": (
                "- **Custom NAV Trends**\n"
                "- **Weighted Performance**\n"
                "- **Volatility**\n"
                "- **GAV Estimate**\n"
            ),
            "How to Use": (
                "1. Select a start date at least 7 days prior.\n"
                "2. Review metrics calculated from the selected date to today.\n"
                "3. Analyze short- to medium-term trends and risk-return dynamics."
            ),
            "Risk-Free Rate": (
                "The risk-free rate represents the theoretical return on an investment with no risk of financial loss. "
                "Typically, this is based on the yield of government bonds, such as U.S. Treasury bills, which are considered "
                "the safest investment. It serves as a benchmark for evaluating the performance of the fund.\n\n"
                "In this chart, the risk-free rate is plotted alongside the fund's NAV to help investors assess the fund's "
                "risk-adjusted returns. By comparing the fund's growth trajectory to the risk-free rate, you can:\n"
                "- Determine the excess return achieved by the fund (also called **alpha**).\n"
                "- Understand whether the fund is outperforming a 'safe' investment over time.\n"
                "- Gauge the justification for the level of risk taken by the fund relative to its return."
            ),

        },
    },
    "expiries" : {
        "key": "expiries_popup",
        "title": "Understanding Option Expiries",
        "button_title": "Learn More About Option Expiries",
        "content_dict": {
            "What are Option Expiries?": (
                "Option expiry refers to the date on which an option contract ceases to exist. "
                "After this date, the contract becomes invalid, and any rights or obligations "
                "associated with the option can no longer be exercised."
            ),
            "Why Does It Matter?": (
                "- **Impact on Portfolio**: As options near expiry, their value is primarily driven by intrinsic value, "
                "and time value diminishes (known as time decay).\n"
                "- **Liquidity Considerations**: Many traders close or roll over positions before expiry to avoid "
                "assignment risks or illiquidity issues.\n"
                "- **Volatility Dynamics**: Expiring options can create increased volatility due to adjustments in hedging activities."
            ),
            "What This Page Displays": (
                "- **Number of Expiries Per Week**: A breakdown of the count of options expiring in each week, "
                "providing an overview of near-term expiries.\n"
                "- **10 Next Expiries**: A quick list of the next 10 expiring options.\n"
                "- **All Positions**: A comprehensive table of all current positions."
            ),
            
        }
    },
    "asset_class_performance": {
        "key": "asset_class_performance_popup",
        "title": "Asset Class Performance Overview",
        "button_title": "Learn More About Asset Class Performance",
        "content_dict": {
            "Overview": (
                "This bar chart provides a detailed overview of the performance of three major asset classes—"
                "**Equity**, **Forex**, and **Vault**. The chart highlights key metrics that give insights into "
                "their contribution to the portfolio's overall performance."
            ),
            "What This Chart Displays": (
                "- **Market Value (MV) Today**: The current market value of the given asset class, reflecting its total worth as of today.\n"
                "- **PnL Variation Since Selected Date**: The change in profit and loss (PnL) of the asset class from the selected date to today. "
                "This helps track the asset class's performance over the specified period.\n"
                "- **NAV Since Selected Date**: The Net Asset Value (NAV) of the asset class, calculated over the period from the selected date to today, "
                "showing its overall contribution to the portfolio."
            ),
            "Why These Metrics Matter": (
                "- **Market Value Today**: Gives a snapshot of the current size and importance of each asset class in the portfolio.\n"
                "- **PnL Variation**: Helps measure the realized and unrealized gains or losses over the chosen period, enabling performance assessment.\n"
                "- **NAV Since Selected Date**: Highlights the cumulative growth or decline of the asset class and its impact on the fund's NAV."
            ),
            "How to Use This Chart": (
                "1. **Compare Across Asset Classes**: Analyze which asset class has contributed the most to portfolio growth or volatility.\n"
                "2. **Understand PnL Variations**: Look at the bars representing PnL to gauge short-term and long-term profitability trends.\n"
                "3. **Evaluate Asset Allocation**: Use the market value data to see if your portfolio is appropriately diversified or overly concentrated "
                "in a specific asset class."
            ),
            "Insights and Actionable Takeaways": (
                "- If an asset class shows significant PnL variation or NAV changes, review the underlying positions to understand the drivers.\n"
                "- Monitor the market value to ensure no single asset class is disproportionately large, as it could increase portfolio risk.\n"
                "- Use this chart to identify opportunities for rebalancing or diversifying your portfolio to optimize performance."
            ),
        },
    },
    
    "mv_distribution": {
        "key": "mv_distribution_popup",
        "title": "Portfolio Composition by Asset Class",
        "button_title": "Learn More About MV Distribution",
        "content_dict": {
            "Overview": (
                "These two graphs provide insights into the distribution of Market Value (MV) across different books "
                "in the portfolio, such as equity, bonds, options, and others. By examining these visualizations, "
                "you can better understand how the portfolio's assets are allocated and weighted."
            ),
            "What These Graphs Display": (
                "- **Bar Chart**: Shows the Market Value (MV) for each book, providing a clear representation of the size of each asset class in absolute terms.\n"
                "- **Pie Chart**: Displays the percentage of each book's Market Value (MV) relative to the total Net Asset Value (NAV) of the portfolio, "
                "indicating the weight or proportion of each asset class in the portfolio."
            ),
            "Why These Metrics Matter": (
                "- **Market Value by Book**: Highlights the contribution of each book to the portfolio, helping identify areas of concentration or underweighting.\n"
                "- **MV/NAV Percentage**: Provides a relative measure of each book's significance within the entire portfolio, enabling better diversification analysis."
            ),
            "How to Use These Graphs": (
                "1. **Analyze Asset Allocation**: Use the bar chart to compare the absolute Market Value across books and identify the largest contributors.\n"
                "2. **Evaluate Portfolio Weighting**: Use the pie chart to understand the relative weighting of each book, ensuring the portfolio is well-diversified.\n"
                "3. **Identify Imbalances**: Look for over-concentration in any single book or underweighting in key asset classes to determine if rebalancing is needed."
            ),
            "Insights and Actionable Takeaways": (
                "- Books with disproportionately high Market Value or weight may pose concentration risks. Consider reducing exposure to manage risk.\n"
                "- Underweighted books could represent missed opportunities for growth or diversification.\n"
                "- Regularly monitoring these metrics can help ensure the portfolio aligns with strategic investment goals and risk tolerance."
            ),
        },
    },
    "leverage_analysis": {
        "key": "leverage_analysis_popup",
        "title": "Leverage Analysis and Distribution",
        "button_title": "Learn More About Leverage Analysis",
        "content_dict": {
            "Overview": (
                "These two graphs provide an in-depth analysis of the fund's leverage, showcasing its evolution over time "
                "and the distribution across different underlying asset classes. Leverage plays a critical role in determining "
                "the fund's risk exposure and growth potential."
            ),
            "What These Graphs Display": (
                "- **Graph 1: Evolution of Commitment and Growth Leverage**:\n"
                "   - Commitment Leverage: Tracks the exposure relative to the portfolio's regulatory or contractual limits, "
                "indicating the fund's adherence to leverage constraints.\n"
                "   - Growth Leverage: Represents the actual utilization of leverage to enhance portfolio growth and returns over time.\n\n"
                "- **Graph 2: Leverage Per Underlying**:\n"
                "   - Shows the allocation of leverage across different underlying asset classes, such as equity, bonds, and forex.\n"
                "   - Helps highlight areas of significant exposure or concentration in the portfolio."
            ),
            "Why These Metrics Matter": (
                "- **Commitment Leverage**: Ensures the fund complies with leverage limits and regulatory guidelines, "
                "while balancing risk exposure.\n"
                "- **Growth Leverage**: Indicates how effectively leverage is being used to enhance returns.\n"
                "- **Leverage Per Underlying**: Identifies potential concentration risks in specific asset classes, which can amplify volatility."
            ),
            "How to Use These Graphs": (
                "1. **Monitor Leverage Trends**: Use the first graph to track changes in commitment and growth leverage over time, "
                "and ensure leverage levels align with the fund's strategy.\n"
                "2. **Evaluate Risk Exposure**: Use the second graph to identify asset classes with disproportionately high leverage allocations, "
                "which may require rebalancing.\n"
                "3. **Align with Objectives**: Ensure leverage levels are consistent with the fund's growth objectives and risk tolerance."
            ),
            "Insights and Actionable Takeaways": (
                "- Rising growth leverage alongside steady commitment leverage indicates efficient use of leverage to drive returns.\n"
                "- Over-concentration of leverage in a single underlying asset class could increase portfolio risk; consider diversifying leverage exposure.\n"
                "- Regularly review leverage metrics to ensure the fund remains compliant with regulatory limits while achieving desired performance goals."
            ),
        },
    },

    "mv_concentration_counterparties": {
        "key": "mv_concentration_counterparties_popup",
        "title": "Market Value Concentration Across Counterparties",
        "button_title": "Learn More About Counterparty MV Concentration",
        "content_dict": {
            "Overview": (
                "These two graphs provide a comprehensive view of the fund's Market Value (MV) allocation across counterparties. "
                "They highlight both the absolute monetary exposure and the relative percentage weight of each counterparty "
                "in the portfolio's Net Asset Value (NAV). Monitoring counterparty concentration is crucial to maintaining compliance "
                "with the 30% MV limit and ensuring balanced risk exposure."
            ),
            "What These Graphs Display": (
                "- **Bar Chart**: Displays the absolute monetary Market Value (MV) held with each counterparty, giving a clear picture of the fund's exposure.\n"
                "- **Pie Chart**: Shows the MV as a percentage of the total NAV, representing the relative weight of each counterparty in the portfolio."
            ),
            "Why This Matters": (
                "- **Regulatory Compliance**: Regulatory guidelines restrict funds from allocating more than 30% of their MV to a single counterparty. "
                "This ensures diversification and reduces systemic risk.\n"
                "- **Risk Mitigation**: High concentration in one counterparty can expose the fund to significant financial risks in the event of counterparty default.\n"
                "- **Portfolio Diversification**: A well-diversified MV distribution across counterparties enhances portfolio stability and minimizes dependency."
            ),
            "How to Use These Graphs": (
                "1. **Analyze Absolute Exposure**: Use the bar chart to identify counterparties with the highest monetary exposure.\n"
                "2. **Evaluate Relative Weight**: Use the pie chart to assess each counterparty's contribution to the portfolio as a percentage of NAV.\n"
                "3. **Ensure Compliance**: Ensure no single counterparty exceeds the 30% MV threshold.\n"
                "4. **Plan Reallocation**: If exposure to a counterparty approaches or exceeds 30%, consider reallocating MV to reduce concentration risk."
            ),
            "Insights and Actionable Takeaways": (
                "- Counterparties with an MV/NAV percentage close to or above 30% pose regulatory and financial risks. "
                "Reallocate exposure to stay compliant and reduce risk.\n"
                "- A balanced distribution across multiple counterparties minimizes dependency on any single counterparty and enhances portfolio resilience.\n"
                "- Regularly monitor these metrics to ensure the fund remains within regulatory limits and maintains a healthy risk profile."
            ),
        },
    },
    "cash_distribution_counterparties": {
        "key": "cash_distribution_counterparties_popup",
        "title": "Cash Distribution Across Counterparties",
        "button_title": "Learn More About Cash Distribution",
        "content_dict": {
            "Overview": (
                "These two graphs provide a comprehensive view of the fund's cash allocation across counterparties and accounts. "
                "They highlight the amount of cash held in different currencies and accounts, offering insights into liquidity distribution and currency diversification."
            ),
            "What These Graphs Display": (
                "- **Stacked Area Chart**: Shows the total cash held across counterparties, broken down by currency, in euros. This visualization allows you to "
                "track how cash is distributed and fluctuates over time across counterparties.\n"
                "- **Detailed Account and Currency Breakdown**: Displays cash amounts for each account and currency. For example, you can see multiple currencies "
                "allocated to specific accounts within each bank, highlighting the diversification of cash holdings."
            ),
            "Why This Matters": (
                "- **Liquidity Management**: Understanding cash distribution helps ensure the fund has sufficient liquidity to meet obligations and seize opportunities.\n"
                "- **Counterparty Risk Management**: Monitoring cash allocation across counterparties reduces the risk of over-concentration in any single institution.\n"
                "- **Currency Diversification**: Holding cash in multiple currencies mitigates exposure to foreign exchange volatility and provides flexibility in cross-border transactions."
            ),
            "How to Use These Graphs": (
                "1. **Analyze Counterparty Allocation**: Use the stacked area chart to assess how cash is distributed across counterparties over time.\n"
                "2. **Review Currency and Account Details**: Use the detailed breakdown to understand which currencies are held in which accounts and with which counterparties.\n"
                "3. **Ensure Diversification**: Check that no single counterparty or currency holds an excessive share of cash to minimize risks.\n"
                "4. **Plan Reallocations**: If needed, consider reallocating cash to balance currency exposure and counterparty concentration."
            ),
            "Insights and Actionable Takeaways": (
                "- Counterparties or accounts with disproportionately large cash holdings could increase risk. Reallocate as necessary to diversify exposure.\n"
                "- Currency imbalances may expose the fund to FX risk. Adjust cash holdings across currencies to align with operational needs and risk appetite.\n"
                "- Regular monitoring ensures the fund maintains adequate liquidity, currency balance, and counterparty diversification."
            ),
        },
    },

    "counterparty_cash_details": {
        "key": "counterparty_cash_details_popup",
        "title": "Counterparty Cash Details and Requirements",
        "button_title": "Learn More About Counterparty Cash Details",
        "content_dict": {
            "Overview": (
                "This table provides a detailed breakdown of the cash-related metrics for each counterparty, including collateral, margins, requirements, "
                "and net excess or deficit. These figures help you assess the cash flow, collateral utilization, and overall liquidity with each counterparty."
            ),
            "What This Table Displays": (
                "- **Total Collateral**: The total amount of collateral held or provided for transactions with the counterparty.\n"
                "- **Initial Margin**: The amount of collateral required to open positions with the counterparty.\n"
                "- **Variation Margin**: The daily mark-to-market adjustments made to reflect changes in the value of positions.\n"
                "- **Requirement**: The total margin requirement, including initial and variation margins.\n"
                "- **Net Excess/Deficit**: The difference between the available cash or collateral and the total requirement. "
                "A positive value indicates excess collateral, while a negative value indicates a deficit that needs to be covered."
            ),
            "Why This Matters": (
                "- **Liquidity Monitoring**: Ensures the fund has sufficient cash or collateral to meet margin requirements with counterparties.\n"
                "- **Risk Management**: Identifies any deficits that could lead to margin calls or trading restrictions.\n"
                "- **Collateral Optimization**: Tracks how collateral is allocated across counterparties to avoid inefficiencies or over-concentration."
            ),
            "How to Use This Table": (
                "1. **Check Net Excess/Deficit**: Monitor each counterparty’s net cash position to ensure there are no significant deficits that require immediate action.\n"
                "2. **Evaluate Collateral Utilization**: Review total collateral and margin requirements to ensure collateral is being used efficiently.\n"
                "3. **Plan Reallocations**: If deficits are observed, reallocate cash or collateral from excess positions to maintain compliance and liquidity.\n"
                "4. **Track Margin Trends**: Use variation margins to assess how changing market conditions are affecting cash flow and liquidity needs."
            ),
            "Insights and Actionable Takeaways": (
                "- A **net deficit** indicates a potential shortfall in cash or collateral, which may require immediate action to avoid margin calls.\n"
                "- Excess collateral at a counterparty may suggest opportunities to reallocate resources to optimize liquidity.\n"
                "- Regularly monitor this table to maintain sufficient liquidity and meet all counterparty requirements efficiently."
            ),
        },
    },

    "collateral_margin_trends": {
        "key": "collateral_margin_trends_popup",
        "title": "Collateral and Margin Trends Across Counterparties",
        "button_title": "Learn More About Collateral and Margin Trends",
        "content_dict": {
            "Overview": (
                "These four charts provide a detailed view of the fund's collateral and margin metrics over time, broken down by counterparty. "
                "Each chart includes multiple lines representing individual counterparties, enabling you to monitor and compare their contributions "
                "to the fund's overall liquidity and risk profile."
            ),
            "What These Charts Display": (
                "- **Initial Margin (IM) Over Time**: Tracks the amount of collateral required to open positions with each counterparty, "
                "showing how requirements evolve over time.\n"
                "- **Total Collateral Over Time**: Displays the total collateral held by each counterparty, helping to visualize allocation trends.\n"
                "- **Variation Margin (VM) Over Time**: Tracks daily mark-to-market adjustments for each counterparty, reflecting changes in position value due to market movements.\n"
                "- **Requirement Over Time**: Shows the total margin requirements (initial + variation) for each counterparty, providing insights into liquidity needs."
            ),
            "Why These Metrics Matter": (
                "- **Initial Margin Trends**: Helps monitor evolving collateral requirements to maintain open positions, especially during market volatility.\n"
                "- **Total Collateral Trends**: Tracks how collateral is allocated across counterparties, highlighting potential inefficiencies or over-concentration.\n"
                "- **Variation Margin Trends**: Reflects the sensitivity of positions to market movements, helping assess the impact of market volatility.\n"
                "- **Requirement Trends**: Shows the fund’s liquidity obligations and ensures there is adequate cash or collateral to meet these demands."
            ),
            "How to Use These Charts": (
                "1. **Compare Counterparty Metrics**: Use the lines on each chart to identify which counterparties have the highest or most volatile metrics.\n"
                "2. **Monitor Collateral Efficiency**: Evaluate total collateral trends to ensure resources are allocated optimally across counterparties.\n"
                "3. **Assess Market Sensitivity**: Use variation margin trends to understand how market movements are affecting counterparty positions.\n"
                "4. **Plan for Liquidity Needs**: Analyze requirement trends to anticipate future liquidity demands and ensure sufficient reserves."
            ),
            "Insights and Actionable Takeaways": (
                "- Significant increases in **Initial Margin** or **Requirement** metrics may indicate rising risk exposure or tightening liquidity conditions.\n"
                "- Counterparties with consistently high **Variation Margin** may warrant closer monitoring to manage market sensitivity effectively.\n"
                "- Efficient collateral allocation across counterparties minimizes concentration risks and ensures compliance with margin requirements.\n"
                "- Regularly review these metrics to maintain a healthy balance between collateral usage, margin requirements, and liquidity reserves."
            ),
        },
    },

    "var_cvar_metrics": {
        "key": "var_cvar_metrics_popup",
        "title": "VaR and CVaR Metrics Overview",
        "button_title": "Learn More About VaR and CVaR",
        "content_dict": {
            "Overview": (
                "This table provides an overview of the fund's risk exposure through Value at Risk (VaR) and Conditional Value at Risk (CVaR) metrics. "
                "Both metrics are displayed at 95% and 99% confidence levels, offering insights into potential losses under normal and extreme conditions."
            ),
            "What This Table Displays": (
                "- **VaR (95% and 99%)**: The maximum expected loss over a given time horizon with a confidence level of 95% or 99%. "
                "For example, a 95% VaR indicates that there is only a 5% chance of losses exceeding this value under normal market conditions.\n"
                "- **CVaR (95% and 99%)**: Also known as Expected Shortfall, this measures the average loss beyond the VaR threshold. "
                "It provides a more comprehensive view of tail risk by considering the severity of losses in extreme scenarios."
            ),
            "Why These Metrics Matter": (
                "- **Risk Assessment**: VaR and CVaR quantify potential losses, enabling the fund to evaluate its risk exposure under normal and stressed market conditions.\n"
                "- **Regulatory Compliance**: Many regulatory frameworks require funds to monitor and report VaR and CVaR as part of their risk management practices.\n"
                "- **Portfolio Optimization**: Understanding the distribution of risk helps in reallocating assets to balance return objectives with acceptable risk levels."
            ),
            "How to Use This Table": (
                "1. **Compare Confidence Levels**: Use the 95% and 99% metrics to understand the range of potential losses under normal and extreme market conditions.\n"
                "2. **Assess Tail Risk**: Focus on CVaR to gauge the severity of losses in the worst-case scenarios and plan mitigation strategies accordingly.\n"
                "3. **Monitor Risk Trends**: Regularly track changes in VaR and CVaR to identify shifts in portfolio risk due to market movements or changes in asset allocation."
            ),
            "Insights and Actionable Takeaways": (
                "- High VaR or CVaR values may indicate elevated risk levels, requiring closer monitoring or rebalancing of the portfolio.\n"
                "- A significant difference between 95% and 99% metrics suggests heightened tail risk, emphasizing the need for stress testing and contingency planning.\n"
                "- Regularly review these metrics to align the fund's risk exposure with its investment strategy and regulatory requirements."
            ),
        },
    },
    "im_mv_counterparty": {
        "key": "im_mv_counterparty_popup",
        "title": "Initial Margin and Market Value by Counterparty",
        "button_title": "Learn More About IM and MV",
        "content_dict": {
            "Overview": (
                "This bar chart provides a comparison of the Initial Margin (IM) and Market Value (MV) across counterparties. "
                "By visualizing these metrics side by side, you can assess the level of collateral required relative to the value of positions held with each counterparty."
            ),
            "What This Chart Displays": (
                "- **Initial Margin (IM)**: The amount of collateral required to open and maintain positions with each counterparty.\n"
                "- **Market Value (MV)**: The total value of positions held with each counterparty, representing the exposure to that counterparty."
            ),
            "Why These Metrics Matter": (
                "- **Risk Assessment**: Comparing IM and MV helps determine whether collateral requirements are proportionate to exposure, "
                "and highlights counterparties with potentially high risk.\n"
                "- **Liquidity Management**: Monitoring IM requirements ensures the fund maintains sufficient liquidity to meet collateral obligations.\n"
                "- **Counterparty Exposure**: The MV metric reflects the concentration of positions with counterparties, which can inform diversification strategies."
            ),
            "How to Use This Chart": (
                "1. **Compare IM and MV**: Identify counterparties where IM is disproportionately high or low compared to MV.\n"
                "2. **Monitor Concentration**: Use MV to assess exposure levels and ensure no single counterparty holds an excessive share of positions.\n"
                "3. **Ensure Liquidity Readiness**: Check IM levels to confirm that the fund has sufficient cash or collateral to meet margin requirements."
            ),
            "Insights and Actionable Takeaways": (
                "- A high MV relative to IM may indicate a more efficient use of collateral, but it could also signal higher risk if exposure is concentrated.\n"
                "- A disproportionately high IM for a counterparty might indicate stricter margin requirements, suggesting a need for better collateral optimization.\n"
                "- Regularly monitoring IM and MV helps ensure the fund maintains a healthy balance between risk exposure and collateral obligations."
            ),
        },
    },
    "time_series_im_mv": {
        "key": "time_series_im_mv_popup",
        "title": "Time Series Analysis of IM and MV by Counterparty",
        "button_title": "Learn More About IM and MV Trends",
        "content_dict": {
            "Overview": (
                "These two time series charts provide a detailed view of the evolution of Initial Margin (IM) and Market Value (MV) "
                "over time for each counterparty. Each line on the charts represents the trend for a specific counterparty, "
                "allowing for a comparative analysis of risk exposure and collateral requirements across counterparties."
            ),
            "What These Charts Display": (
                "- **IM Over Time**: Tracks the changes in Initial Margin requirements for each counterparty over the selected period. "
                "This metric reflects how collateral demands evolve based on market movements, position sizes, or changes in counterparty terms.\n"
                "- **MV Over Time**: Shows the changes in Market Value of positions held with each counterparty, illustrating how exposure levels "
                "vary over time due to portfolio adjustments or market fluctuations."
            ),
            "Why These Metrics Matter": (
                "- **Initial Margin Trends**: Monitoring IM over time ensures that the fund maintains sufficient liquidity to meet collateral demands, "
                "particularly during periods of market stress.\n"
                "- **Market Value Trends**: Tracking MV provides insights into the portfolio's exposure to counterparties and helps identify periods "
                "of increased or decreased concentration risk.\n"
                "- **Counterparty Comparisons**: Comparing trends across counterparties highlights differences in risk exposure and collateral requirements, "
                "informing diversification and risk management strategies."
            ),
            "How to Use These Charts": (
                "1. **Analyze Individual Counterparties**: Identify counterparties with consistently high or volatile IM and MV values, which may signal increased risk exposure.\n"
                "2. **Monitor Trends Over Time**: Look for patterns such as rising IM during periods of market stress or fluctuations in MV due to portfolio changes.\n"
                "3. **Assess Counterparty Balance**: Compare trends across counterparties to ensure no single counterparty dominates in terms of collateral or exposure.\n"
                "4. **Plan for Liquidity**: Use IM trends to anticipate future liquidity needs and ensure the fund is prepared for potential margin calls."
            ),
            "Insights and Actionable Takeaways": (
                "- Rapid increases in IM for specific counterparties may indicate tightening collateral requirements or rising market volatility.\n"
                "- Significant fluctuations in MV suggest changes in portfolio composition or market dynamics, requiring closer monitoring.\n"
                "- Regularly review these trends to maintain a balanced counterparty exposure and ensure adequate liquidity for margin obligations."
            ),
        },
    },
    "comparison_ice_counterparty": {
        "key": "comparison_ice_counterparty_popup",
        "title": "Comparison of IM and MV: ICE vs. Counterparty Data",
        "button_title": "Learn More About IM and MV Comparison",
        "content_dict": {
            "Overview": (
                "These two graphs provide a comparison between the Initial Margin (IM) and Market Value (MV) calculated using ICE Data Derivatives "
                "and the values reported by counterparties through email. The charts can be filtered to focus on a specific counterparty or show the total IM/MV across all counterparties."
            ),
            "What These Graphs Display": (
                "- **Graph 1: Initial Margin (IM) Comparison**:\n"
                "   - Displays the total IM as calculated by ICE Data Derivatives and compares it to the IM reported by counterparties.\n"
                "- **Graph 2: Market Value (MV) Comparison**:\n"
                "   - Shows the total MV derived from ICE Data Derivatives and compares it to the MV reported by counterparties.\n"
                "- **Filtering Options**:\n"
                "   - Choose a specific counterparty to analyze discrepancies between ICE and counterparty-provided values.\n"
                "   - Select 'Total' to view the aggregate IM or MV across all counterparties."
            ),
            "Why These Metrics Matter": (
                "- **Data Validation**: Comparing ICE-calculated values with counterparty-reported data helps ensure the accuracy and consistency of risk metrics.\n"
                "- **Risk Management**: Identifies discrepancies that may signal reporting errors, miscalculations, or potential risks in collateral and position data.\n"
                "- **Transparency**: Provides an additional layer of oversight by cross-referencing independent calculations with counterparty reports."
            ),
            "How to Use These Graphs": (
                "1. **Filter by Counterparty**: Use the filter to focus on individual counterparties and compare their reported IM/MV to ICE-calculated values.\n"
                "2. **Analyze Discrepancies**: Look for significant differences between ICE and counterparty data to identify inconsistencies.\n"
                "3. **Check Totals**: Select 'Total' to view the aggregate IM or MV and ensure overall consistency between ICE and counterparty reports.\n"
                "4. **Investigate Outliers**: If discrepancies are found, follow up with counterparties to understand the reasons and resolve any issues."
            ),
            "Insights and Actionable Takeaways": (
                "- Large discrepancies between ICE and counterparty-reported values may indicate reporting errors or differences in calculation methodologies.\n"
                "- Persistent differences with a specific counterparty should be investigated further to ensure accurate reporting.\n"
                "- Regularly comparing ICE-derived and counterparty-reported values improves confidence in the fund's margin and market value data."
            ),
        },
    },
    "delta_gamma_assets": {
        "key": "delta_gamma_assets_popup",
        "title": "Delta and Gamma by Asset",
        "button_title": "Learn More About Delta and Gamma",
        "content_dict": {
            "Overview": (
                "This bar chart provides a breakdown of Delta and Gamma for each asset in the portfolio. "
                "These metrics offer insights into the portfolio’s sensitivity to changes in the underlying market prices (Delta) and "
                "the rate of change of Delta with respect to price movements (Gamma)."
            ),
            "What This Chart Displays": (
                "- **Delta**: Measures the sensitivity of an asset's value to changes in the price of its underlying asset. "
                "A positive Delta indicates that the asset's value will increase as the underlying price rises, while a negative Delta indicates the opposite.\n"
                "- **Gamma**: Represents the rate of change of Delta as the underlying asset price changes. "
                "Higher Gamma values suggest that Delta is more sensitive to price movements, indicating potential volatility."
            ),
            "Why These Metrics Matter": (
                "- **Portfolio Hedging**: Delta helps determine the hedging requirements for the portfolio to maintain neutrality against market movements.\n"
                "- **Risk Management**: Gamma highlights the potential for large changes in Delta, signaling areas of increased risk or opportunity.\n"
                "- **Asset Sensitivity**: Understanding Delta and Gamma at the asset level enables better management of exposure to market fluctuations."
            ),
            "How to Use This Chart": (
                "1. **Analyze Asset-Level Sensitivities**: Use the chart to identify assets with high Delta or Gamma values that contribute significantly to portfolio risk.\n"
                "2. **Evaluate Hedging Needs**: Monitor Delta values to ensure the portfolio remains balanced and aligned with its investment strategy.\n"
                "3. **Assess Volatility Exposure**: Use Gamma to identify assets that may experience significant changes in Delta due to price volatility, and adjust positions as needed.\n"
                "4. **Optimize Portfolio**: Compare Delta and Gamma across assets to identify potential opportunities for rebalancing or risk reduction."
            ),
            "Insights and Actionable Takeaways": (
                "- Assets with high Delta values indicate significant exposure to market price changes, which may require hedging adjustments.\n"
                "- High Gamma values suggest potential volatility in Delta, highlighting areas of the portfolio that may require closer monitoring.\n"
                "- Regularly reviewing Delta and Gamma metrics helps maintain a balanced portfolio and align risk exposure with the fund’s objectives."
            ),
        },
    },
    "cross_delta_gamma": {
        "key": "cross_delta_gamma_popup",
        "title": "Cross Delta and Gamma by Asset Pairs",
        "button_title": "Learn More About Cross Delta and Gamma",
        "content_dict": {
            "Overview": (
                "These tables provide a double-entry matrix view of the cross Delta and cross Gamma for pairs of assets in the portfolio. "
                "Cross Delta and Gamma measure the combined sensitivities of asset pairs to changes in market prices, offering insights "
                "into how these relationships contribute to portfolio risk and performance."
            ),
            "What These Tables Display": (
                "- **Cross Delta**: Represents the sensitivity of the portfolio's value to changes in the prices of two assets in the pair. "
                "Positive or negative cross Delta indicates how a price movement in one asset affects the combined value of the pair.\n"
                "- **Cross Gamma**: Reflects the rate of change of cross Delta as the prices of the two assets in the pair change. "
                "Higher cross Gamma values suggest that the relationship between the assets is more sensitive to price movements, "
                "indicating areas of potential volatility."
            ),
            "Why These Metrics Matter": (
                "- **Risk Assessment**: Cross Delta and Gamma reveal interdependencies between asset pairs, helping identify sources of correlated risk.\n"
                "- **Portfolio Optimization**: Understanding the sensitivities between asset pairs allows for better hedging and diversification strategies.\n"
                "- **Market Dynamics**: These metrics provide deeper insights into how market movements affect the combined value of related assets."
            ),
            "How to Use These Tables": (
                "1. **Analyze High Sensitivity Pairs**: Identify asset pairs with large cross Delta or cross Gamma values, which may contribute significantly to portfolio risk.\n"
                "2. **Evaluate Risk Concentration**: Focus on pairs with high positive or negative cross Delta to manage correlated exposures.\n"
                "3. **Adjust Hedging Strategies**: Use cross Gamma to assess the need for adjustments in hedging strategies for assets with volatile relationships.\n"
                "4. **Monitor Changes Over Time**: Regularly review these metrics to track changes in asset pair relationships and update portfolio strategies accordingly."
            ),
            "Insights and Actionable Takeaways": (
                "- Asset pairs with high cross Delta may require additional hedging to mitigate combined exposure to price movements.\n"
                "- High cross Gamma values suggest potential for large changes in sensitivity, indicating areas of increased volatility.\n"
                "- Regular monitoring of cross Delta and Gamma metrics supports better risk management and enhances portfolio stability."
            ),
        },
    },
    "delta_stress_scenarios": {
        "key": "delta_stress_scenarios_popup",
        "title": "Delta Stress Scenarios Across Sigma Levels",
        "button_title": "Learn More About Delta Stress Scenarios",
        "content_dict": {
            "Overview": (
                "These tables display the results of Delta stress test scenarios, evaluating the portfolio's performance under market shifts ranging "
                "from -3σ to +3σ. The analysis is presented from three perspectives: P&L, percentage of NAV (%NAV), and Delta. Each table provides "
                "a detailed breakdown of the stress results for individual assets."
            ),
            "What These Tables Display": (
                "- **Table 1: Delta Stress Scenarios**:\n"
                "   - Shows the projected profit or loss (in monetary terms) for each asset under stress scenarios ranging from -3σ to +3σ.\n"
                "- **Table 2: Delta Stress Nav (%)**:\n"
                "   - Represents the stress results as a percentage of the portfolio's Net Asset Value (NAV), highlighting relative impacts on the portfolio.\n"
                "- **Table 3: Delta Stress Absolute**:\n"
                "   - Displays the Delta for each asset under the same stress scenarios, illustrating the portfolio's sensitivity to price movements."
            ),
            "Why These Metrics Matter": (
                "- **Stress Testing**: Evaluates the portfolio's resilience to extreme market movements and identifies potential vulnerabilities.\n"
                "- **Risk Management**: Provides insights into the monetary, proportional, and sensitivity impacts of stress scenarios on individual assets.\n"
                "- **Portfolio Optimization**: Helps assess which assets contribute the most to stress impacts and where rebalancing or hedging may be required."
            ),
            "How to Use These Tables": (
                "1. **Analyze P&L Results**: Use the first table to evaluate the absolute profit or loss for each asset under stress scenarios.\n"
                "2. **Assess Relative Impact on NAV**: Use the second table to understand how stress scenarios affect the portfolio's NAV, highlighting key contributors.\n"
                "3. **Examine Delta Sensitivity**: Use the third table to track how asset sensitivities (Delta) change under different sigma levels.\n"
                "4. **Identify High-Risk Assets**: Focus on assets with significant stress impacts (P&L, %NAV, or Delta) and plan hedging or rebalancing strategies accordingly."
            ),
            "Insights and Actionable Takeaways": (
                "- Assets with large losses in the P&L table may require closer monitoring or additional hedging.\n"
                "- Significant impacts on %NAV highlight assets that have a disproportionate effect on portfolio performance and require diversification or mitigation strategies.\n"
                "- Changes in Delta under stress scenarios provide insights into portfolio sensitivity and can guide adjustments to risk exposure.\n"
                "- Regularly running stress scenarios helps ensure the portfolio remains resilient to extreme market movements."
            ),
        },
    },
    "risk_metrics_sensitivities": {
        "key": "risk_metrics_sensitivities_popup",
        "title": "Portfolio Risk Metrics and Sensitivities",
        "button_title": "Learn More About Risk Metrics",
        "content_dict": {
            "Overview": (
                "This table provides an overview of key risk metrics and sensitivities for all assets in the portfolio, including Gamma, Theta, "
                "P&L per 1σ and 3σ shifts, and the standard deviation (Std) of asset returns. These metrics collectively offer a detailed view of "
                "the portfolio's exposure to market movements and its risk profile."
            ),
            "What This Table Displays": (
                "- **Gamma**: Measures the rate of change of Delta with respect to changes in the price of the underlying asset. "
                "Higher Gamma indicates greater sensitivity of Delta to price changes, highlighting areas of potential volatility.\n"
                "- **Theta**: Represents the time decay of an asset's value, indicating the amount of value the asset loses as time passes.\n"
                "- **P&L per 1σ**: Shows the projected profit or loss for a 1 standard deviation change in the price of the underlying asset.\n"
                "- **P&L per 3σ**: Reflects the projected profit or loss for a 3 standard deviation change, representing extreme market scenarios.\n"
                "- **Standard Deviation (Std)**: Measures the historical volatility of an asset’s returns, providing insights into its inherent risk."
            ),
            "Why These Metrics Matter": (
                "- **Gamma and Theta**: Together, they provide insights into the sensitivity and time-decay characteristics of assets, helping optimize hedging and risk strategies.\n"
                "- **P&L per 1σ and 3σ**: Highlight the portfolio’s expected performance under normal and extreme market conditions, aiding stress testing.\n"
                "- **Standard Deviation**: Offers a measure of historical volatility, indicating the inherent riskiness of each asset."
            ),
            "How to Use This Table": (
                "1. **Monitor High Gamma Assets**: Identify assets with high Gamma values, which may require additional monitoring or hedging due to their sensitivity to price changes.\n"
                "2. **Assess Time Decay**: Use Theta to evaluate the impact of time on asset value, especially for options, and plan accordingly to minimize losses.\n"
                "3. **Evaluate Stress Scenarios**: Compare P&L per 1σ and 3σ to understand how assets are expected to perform under normal and extreme conditions.\n"
                "4. **Review Volatility**: Use standard deviation to assess asset-specific risk and decide on diversification or rebalancing strategies."
            ),
            "Insights and Actionable Takeaways": (
                "- Assets with high Gamma values may require hedging to mitigate sudden changes in Delta due to price movements.\n"
                "- Significant negative Theta values indicate time-decay risks, which could erode portfolio value over time.\n"
                "- Large P&L variations for 3σ scenarios highlight assets contributing most to tail risk, requiring closer scrutiny.\n"
                "- Regular monitoring of these metrics supports effective risk management and ensures the portfolio remains aligned with strategic objectives."
            ),
        },
    },

    "equity_fx_risk_metrics": {
        "key": "equity_fx_risk_metrics_popup",
        "title": "Equity and FX Risk Metrics",
        "button_title": "Learn More About Equity and FX Risk",
        "content_dict": {
            "Overview": (
                "This table provides a detailed breakdown of key risk metrics for each equity and FX asset in the portfolio. "
                "The metrics include Delta, Gamma, Vega, Theta, and their respective contributions to the portfolio's Net Asset Value (NAV). "
                "These insights help assess the portfolio's sensitivity to market movements and its overall risk profile."
            ),
            "What This Table Displays": (
                "- **Delta**: Measures the sensitivity of the asset’s value to changes in the price of the underlying asset.\n"
                "- **Gamma**: Represents the rate of change of Delta as the underlying asset price changes, indicating sensitivity to price volatility.\n"
                "- **Vega**: Measures the sensitivity of the asset’s value to changes in implied volatility of the underlying asset.\n"
                "- **Theta**: Indicates the time decay of the asset’s value, showing how much value the asset loses as time passes.\n"
                "- **Delta %NAV**: Delta expressed as a percentage of the portfolio’s Net Asset Value, reflecting its relative impact on the portfolio.\n"
                "- **Gamma %NAV**: Gamma expressed as a percentage of NAV, indicating the asset’s contribution to portfolio volatility.\n"
                "- **Vega %NAV**: Vega as a percentage of NAV, highlighting the portfolio’s exposure to changes in implied volatility.\n"
                "- **Theta %NAV**: Theta as a percentage of NAV, reflecting the time decay impact on the portfolio."
            ),
            "Why These Metrics Matter": (
                "- **Sensitivity Analysis**: Delta, Gamma, Vega, and Theta provide a comprehensive view of the portfolio’s sensitivity to market price, volatility, and time.\n"
                "- **NAV Contribution**: Expressing these metrics as percentages of NAV allows for an assessment of their relative importance and potential impact on the portfolio.\n"
                "- **Risk Management**: Understanding these metrics helps identify assets that contribute significantly to portfolio risk, aiding in hedging and diversification decisions."
            ),
            "How to Use This Table": (
                "1. **Monitor Key Metrics**: Focus on assets with high Delta, Gamma, Vega, or Theta values to identify significant sources of sensitivity or risk.\n"
                "2. **Evaluate NAV Contributions**: Use the %NAV metrics to assess the proportional impact of each asset on the portfolio's risk profile.\n"
                "3. **Balance Risk Exposure**: Rebalance assets with disproportionately high contributions to Delta %NAV, Gamma %NAV, or Vega %NAV to mitigate risk.\n"
                "4. **Plan for Time Decay**: Address assets with significant Theta %NAV to minimize losses due to time decay."
            ),
            "Insights and Actionable Takeaways": (
                "- High Delta %NAV or Gamma %NAV indicates significant price sensitivity, requiring potential hedging or adjustments.\n"
                "- Large Vega %NAV suggests exposure to changes in implied volatility, which may necessitate volatility hedging strategies.\n"
                "- Significant Theta %NAV indicates time decay risks, especially for options, requiring careful management of positions.\n"
                "- Regular monitoring of these metrics helps maintain a balanced portfolio and align risk exposure with investment objectives."
            ),
        },
    },
    "credit_risk_metrics": {
        "key": "credit_risk_metrics_popup",
        "title": "Credit Risk Metrics: CS01 and CS01 %NAV",
        "button_title": "Learn More About Credit Risk",
        "content_dict": {
            "Overview": (
                "This table provides a detailed breakdown of credit risk metrics for bonds in the portfolio, specifically Credit Spread 01 (CS01) "
                "and CS01 as a percentage of the portfolio's Net Asset Value (NAV). These metrics are critical for understanding the portfolio’s sensitivity "
                "to changes in credit spreads and its exposure to credit risk."
            ),
            "What This Table Displays": (
                "- **CS01**: Represents the sensitivity of the bond’s value to a 1 basis point (0.01%) change in its credit spread. "
                "A higher CS01 indicates greater exposure to changes in credit spreads.\n"
                "- **CS01 %NAV**: Shows the bond’s CS01 as a percentage of the portfolio’s NAV, providing a relative measure of credit risk contribution "
                "for each bond in the portfolio."
            ),
            "Why These Metrics Matter": (
                "- **Credit Spread Sensitivity**: CS01 measures the portfolio’s exposure to changes in credit spreads, which are influenced by credit risk perceptions in the market.\n"
                "- **NAV Contribution**: Expressing CS01 as a percentage of NAV helps assess the relative importance of each bond’s credit risk in the context of the entire portfolio.\n"
                "- **Risk Management**: Understanding CS01 and its contribution to NAV supports proactive management of credit risk and ensures compliance with portfolio objectives."
            ),
            "How to Use This Table": (
                "1. **Monitor High CS01 Bonds**: Identify bonds with high CS01 values to understand which positions are most sensitive to changes in credit spreads.\n"
                "2. **Evaluate NAV Impact**: Use CS01 %NAV to determine the proportional impact of each bond’s credit risk on the overall portfolio.\n"
                "3. **Diversify Credit Risk**: Rebalance or adjust positions in bonds with disproportionately high CS01 %NAV contributions to mitigate credit concentration risk.\n"
                "4. **Track Market Trends**: Use CS01 to gauge how market-wide credit spread movements could affect portfolio performance."
            ),
            "Insights and Actionable Takeaways": (
                "- Bonds with high CS01 or CS01 %NAV values may require closer monitoring or adjustments to balance portfolio risk.\n"
                "- Large contributions to CS01 %NAV from individual bonds indicate potential concentration risks, suggesting the need for diversification.\n"
                "- Regularly reviewing these metrics ensures the portfolio maintains an appropriate level of credit risk exposure aligned with its strategy."
            ),
        },
    },
    "vega_stress_pnl": {
        "key": "vega_stress_pnl_popup",
        "title": "Vega Stress Scenarios and P&L Impact",
        "button_title": "Learn More About Vega Stress Scenarios",
        "content_dict": {
            "Overview": (
                "This table provides a detailed breakdown of Vega and its projected P&L impact under different stress scenarios for each asset in the portfolio. "
                "Vega measures the sensitivity of an asset's value to changes in implied volatility, and this analysis evaluates potential outcomes under "
                "moderate, stress, and extreme market conditions."
            ),
            "What This Table Displays": (
                "- **Vega**: Represents the sensitivity of the asset’s value to a 1% change in implied volatility of the underlying asset.\n"
                "- **Vega P&L (Moderate Scenario)**: Projects the P&L impact for each asset under a moderate increase or decrease in implied volatility.\n"
                "- **Vega P&L (Stress Scenario)**: Estimates the P&L impact for each asset under significant stress in implied volatility.\n"
                "- **Vega P&L (Extreme Scenario)**: Reflects the projected P&L impact under extreme changes in implied volatility, simulating tail risk conditions."
            ),
            "Why These Metrics Matter": (
                "- **Volatility Risk Assessment**: Vega measures the portfolio’s exposure to changes in implied volatility, a key driver of option pricing.\n"
                "- **Stress Testing**: Evaluating Vega P&L under different scenarios helps identify potential vulnerabilities in volatile market conditions.\n"
                "- **Portfolio Optimization**: Understanding Vega and its P&L impact guides adjustments to asset allocation and hedging strategies to manage volatility risk."
            ),
            "How to Use This Table": (
                "1. **Identify High Vega Assets**: Focus on assets with large Vega values, which are highly sensitive to changes in implied volatility.\n"
                "2. **Analyze Scenario-Specific Risks**: Compare P&L impacts across moderate, stress, and extreme scenarios to evaluate asset-specific risks.\n"
                "3. **Hedge Volatility Risk**: Use the insights to plan volatility hedging strategies, especially for assets with high stress or extreme scenario P&L impacts.\n"
                "4. **Optimize Portfolio Volatility Exposure**: Reallocate positions if necessary to maintain a balanced risk profile and avoid concentration in high Vega assets."
            ),
            "Insights and Actionable Takeaways": (
                "- Significant Vega or P&L impacts in extreme scenarios indicate potential tail risks, requiring closer monitoring or mitigation.\n"
                "- Assets with large P&L impacts under stress scenarios may need hedging or diversification to reduce volatility risk.\n"
                "- Regularly evaluating Vega and stress P&L metrics supports effective risk management and enhances portfolio resilience to market fluctuations."
            ),
        },
    },
    "vega_bucket": {
        "key": "vega_bucket_popup",
        "title": "Vega Exposure by Time Buckets",
        "button_title": "Learn More About Vega Buckets",
        "content_dict": {
            "Overview": (
                "This table provides a breakdown of Vega exposure across different time buckets for each asset in the portfolio. "
                "The time buckets range from short-term (1 week) to long-term (>1 year) maturities, along with a total Vega value for each asset. "
                "This analysis helps assess how the portfolio’s volatility sensitivity is distributed over time."
            ),
            "What This Table Displays": (
                "- **1w**: Vega exposure for options maturing within 1 week.\n"
                "- **1w-1m**: Vega exposure for options maturing between 1 week and 1 month.\n"
                "- **1m-3m**: Vega exposure for options maturing between 1 and 3 months.\n"
                "- **3m-6m**: Vega exposure for options maturing between 3 and 6 months.\n"
                "- **6m-1y**: Vega exposure for options maturing between 6 months and 1 year.\n"
                "- **>1y**: Vega exposure for options maturing beyond 1 year.\n"
                "- **Total**: The sum of Vega values across all time buckets for each asset."
            ),
            "Why These Metrics Matter": (
                "- **Volatility Risk Distribution**: Understanding Vega across time buckets helps evaluate how sensitivity to implied volatility is distributed "
                "over different maturities.\n"
                "- **Portfolio Hedging**: Time-based Vega distribution aids in designing effective hedging strategies tailored to specific maturities.\n"
                "- **Risk Concentration**: Identifying concentrated Vega in certain time buckets helps manage exposure and reduce risk."
            ),
            "How to Use This Table": (
                "1. **Analyze Short-Term vs. Long-Term Exposure**: Compare Vega values across time buckets to understand whether the portfolio is more sensitive to "
                "short-term or long-term volatility shifts.\n"
                "2. **Monitor High Vega Assets**: Focus on assets with significant Vega exposure in specific buckets and assess their contribution to overall risk.\n"
                "3. **Plan for Hedging**: Use the time-bucket breakdown to design targeted hedging strategies for short-term or long-term volatility risks.\n"
                "4. **Assess Total Vega**: Review the total Vega values to understand each asset’s overall contribution to the portfolio’s volatility sensitivity."
            ),
            "Insights and Actionable Takeaways": (
                "- High Vega in short-term buckets (e.g., 1w or 1w-1m) indicates sensitivity to immediate market volatility, requiring closer monitoring or short-term hedges.\n"
                "- Significant Vega in long-term buckets (>1y) suggests exposure to long-term volatility changes, which may require rebalancing or longer-term hedging strategies.\n"
                "- Reviewing total Vega alongside its distribution helps identify assets that contribute the most to the portfolio’s overall volatility risk."
            ),
        },
    },
}