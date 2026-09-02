// @version=6
indicator("Swing Pro: MACD Div CONFIRMÉE ONLY + MM50 [Long]", shorttitle="SwingPro CONFIRMED", overlay=true, max_labels_count=500, max_lines_count=500)

// ── نفس الباراميترز لي في تصاورك ──
leftBars = input.int(2, "Bougies à gauche du pivot", minval=1, group="Pivots (Support / Résistance)")
rightBars = input.int(2, "Bougies à droite du pivot", minval=1, group="Pivots (Support / Résistance)")

fastLen = input.int(12, "MACD Rapide", group="MACD & Divergence")
slowLen = input.int(26, "MACD Lente", group="MACD & Divergence")
sigLen = input.int(9, "MACD Signal", group="MACD & Divergence")
firstLookbackBull = input.int(10, "Recherche 1er pivot récent", minval=1, group="MACD & Divergence")
lowerLowLookbackBull = input.int(30, "Recherche 2nd pivot ancien", minval=1, group="MACD & Divergence")
showDivLines = input.bool(true, "Afficher lignes de divergence", group="MACD & Divergence")
requireMacdNeg = input.bool(false, "Exiger MACD < 0 pour la divergence", group="MACD & Divergence")

useSma = input.bool(true, "Filtrer avec MM200", group="Filtre Tendance")
smaLen = input.int(50, "Période MM", group="Filtre Tendance")

confBars = input.int(2, "Bougies de confirmation cassure", minval=1, group="Filtre Cassure (Breakout)")

// ── الحسابات ──
[macdLine, signalLine, histLine] = ta.macd(close, fastLen, slowLen, sigLen)
ma = ta.sma(close, smaLen)
isAboveSma = not useSma or close > ma

pl = ta.pivotlow(low, leftBars, rightBars)

// ── البحث غير على الكونفيرمي BLUE ──
var line[] divLines = array.new_line()
var label[] divLabels = array.new_label()

bullDetected = false
p1_idx = 0
p2_idx = 0

for i = 1 to firstLookbackBull
    if bullDetected
        break
    if not na(pl[i])
        // هذا هو شرط الكونفيرماسيون - لازم الشمعة الحالية تكسر هاي تاع البيفوت
        condBreakout = low[0] > high[i + rightBars] and low[1] <= high[i + rightBars]
        if condBreakout
            p1 = i + rightBars
            for j = i + 1 to i + lowerLowLookbackBull
                if not na(pl[j])
                    p2 = j + rightBars
                    condMacd = requireMacdNeg? (macdLine[p1] > macdLine[p2] and macdLine[p1] < 0) : (macdLine[p1] > macdLine[p2])
                    // Low جديد اقل من القديم + MACD اعلى + فوق MM50
                    if low[p1] < low[p2] and condMacd and isAboveSma
                        bullDetected := true
                        p1_idx := p1
                        p2_idx := p2
                        break

if bullDetected and showDivLines
    // رسم الخط الازرق
    array.push(divLines, line.new(bar_index[p2_idx], low[p2_idx], bar_index[p1_idx], low[p1_idx], color=color.blue, width=2))
    array.push(divLabels, label.new(bar_index[p1_idx], low[p1_idx], "DIV BLUE", style=label.style_label_up, color=color.blue, textcolor=color.white))
    // تنبيه للبوت
    alert("DIV BLUE CONFIRMEE - " + syminfo.ticker + " " + timeframe.period, alert.freq_once_per_bar_close)

plot(useSma? ma : na, "MM50", color=color.white, linewidth=2)
