var startPosition = [
    [1, 1, 0],
    [1, 0, 2],
    [0, 2, 2]
];

var position = document.querySelectorAll(".position");
var turn = document.querySelector(".container");

var player = "p1";

for (var elmt of position) {
    var temp,
        from;

    elmt.addEventListener("click", function (e) {

        if (!turn.classList.contains("moving")) {

            if (turn.classList.contains("player1")) {

                if (this.classList.contains("p1")) {
                    from = this.id;

                    this.classList.remove("p1");
                    this.classList.add("active-p1");
                    temp = this;

                    turn.classList.add("moving");
                } else {
                    alert("Autour de la case rouge!");
                }

            }

        } else {

            if (turn.classList.contains("player1")) {

                if (this != temp) {

                    if (!this.classList.contains("p1") && !this.classList.contains("p2") && isValid(from, this.id)) {
                        moveTo(from, this.id);

                        this.classList.add("p1");

                        temp.classList.remove("active-p1");

                        turn.classList.remove("moving");
                        turn.classList.remove("player1");
                        turn.classList.add("player2");

                        if (gameOver(1)) {
                            alert("Les rouges ont gagné!");
                            window.location.reload();
                        } else {
                            setTimeout(aiMove, 500); // Let AI make a move after a short delay
                        }
                    } else {
                        alert("Déplacement illegal!");
                    }

                } else {
                    this.classList.add("p1");
                    this.classList.remove("active-p1");

                    turn.classList.remove("moving");
                }

            }

        }

    }, false);
}

function aiMove() {
    var bestMove = getBestMove();
    if (bestMove) {
        moveTo(bestMove.from, bestMove.to);
        console.log(bestMove.from,"+", bestMove.to);
        document.getElementById(bestMove.to).classList.add("p2");
        document.getElementById(bestMove.from).classList.remove("p2");

        turn.classList.remove("moving");
        turn.classList.remove("player2");
        turn.classList.add("player1");

        if (gameOver(2)) {
            alert("Les bleus ont gagné!");
            window.location.reload();
        }
    }
}

function getBestMove() {
    var bestScore = -Infinity;
    var move = null;

    for (var i = 0; i < 3; i++) {
        for (var j = 0; j < 3; j++) {
            if (startPosition[i][j] == 2) {
                var moves = getValidMoves(i, j);
                for (var k = 0; k < moves.length; k++) {
                    var [x, y] = moves[k];
                    var temp = startPosition[x][y];
                    startPosition[x][y] = 2;
                    startPosition[i][j] = 0;
                    var score = alphaBeta(startPosition, 0, -Infinity, Infinity, false);
                    startPosition[x][y] = temp;
                    startPosition[i][j] = 2;
                    if (score > bestScore) {
                        bestScore = score;
                        move = { from: `c-${i}${j}`, to: `c-${x}${y}` };
                    }
                }
            }
        }
    }

    return move;
}

function alphaBeta(board, depth, alpha, beta, isMaximizing) {
    if (gameOver(1)) return -10;
    if (gameOver(2)) return 10;
    if (depth == 3) return 0;

    if (isMaximizing) {
        var maxEval = -Infinity;
        for (var i = 0; i < 3; i++) {
            for (var j = 0; j < 3; j++) {
                if (board[i][j] == 2) {
                    var moves = getValidMoves(i, j);
                    for (var k = 0; k < moves.length; k++) {
                        var [x, y] = moves[k];
                        var temp = board[x][y];
                        board[x][y] = 2;
                        board[i][j] = 0;
                        var eval = alphaBeta(board, depth + 1, alpha, beta, false);
                        board[x][y] = temp;
                        board[i][j] = 2;
                        maxEval = Math.max(maxEval, eval);
                        alpha = Math.max(alpha, eval);
                        if (beta <= alpha) break;
                    }
                }
            }
        }
        return maxEval;
    } else {
        var minEval = Infinity;
        for (var i = 0; i < 3; i++) {
            for (var j = 0; j < 3; j++) {
                if (board[i][j] == 1) {
                    var moves = getValidMoves(i, j);
                    for (var k = 0; k < moves.length; k++) {
                        var [x, y] = moves[k];
                        var temp = board[x][y];
                        board[x][y] = 1;
                        board[i][j] = 0;
                        var eval = alphaBeta(board, depth + 1, alpha, beta, true);
                        board[x][y] = temp;
                        board[i][j] = 1;
                        minEval = Math.min(minEval, eval);
                        beta = Math.min(beta, eval);
                        if (beta <= alpha) break;
                    }
                }
            }
        }
        return minEval;
    }
}

function getValidMoves(i, j) {
    var moves = [];
    if (i > 0 && startPosition[i - 1][j] == 0) moves.push([i - 1, j]);
    if (i < 2 && startPosition[i + 1][j] == 0) moves.push([i + 1, j]);
    if (j > 0 && startPosition[i][j - 1] == 0) moves.push([i, j - 1]);
    if (j < 2 && startPosition[i][j + 1] == 0) moves.push([i, j + 1]);
    return moves;
}

function moveTo(id1, id2) {
    var start = id1.split("-")[1].split("");
    var end = id2.split("-")[1].split("");

    if (startPosition[end[0]][end[1]] != 0) {
        console.log("Erreur!!")
        return;
    }

    startPosition[end[0]][end[1]] = startPosition[start[0]][start[1]];
    startPosition[start[0]][start[1]] = 0;
}

function display() {
    for (var i = 0; i < 3; i++) {
        console.log(startPosition[i][0], " ", startPosition[i][1], " ", startPosition[i][2]);
    }
}

function isValid(id1, id2) {
    var start = id1.split("-")[1];
    var end = id2.split("-")[1];

    // Ampovony
    if (start === "11")
        return true;

    // Sisiny
    if (start === "00") {
        if (end === "01" || end === "10" || end === "11")
            return true;
    }

    if (start === "02") {
        if (end === "01" || end === "12" || end === "11")
            return true;
    }

    if (start === "20") {
        if (end === "21" || end === "10" || end === "11")
            return true;
    }

    if (start === "22") {
        if (end === "21" || end === "12" || end === "11")
            return true;
    }

    // Mijanona
    if (start === "01") {
        if (end === "00" || end === "02" || end === "11")
            return true;
    }

    if (start === "10") {
        if (end === "00" || end === "20" || end === "11")
            return true;
    }

    if (start === "21") {
        if (end === "20" || end === "22" || end === "11")
            return true;
    }

    if (start === "12") {
        if (end === "02" || end === "22" || end === "11")
            return true;
    }

    return false;
}

function isAlignedX(x) {
    var compt = 0;

    for (var i = 0; i < 3; i++) {
        for (var j = 0; j < 3; j++) {
            if (startPosition[i][j] == x) {
                compt++;
            }
        }
        if (compt == 3) {
            return true;
        }
        compt = 0;
    }

    return false;
}

function isAlignedY(x) {
    var compt = 0;

    for (var i = 0; i < 3; i++) {
        for (var j = 0; j < 3; j++) {
            if (startPosition[j][i] == x) {
                compt++;
            }
        }
        if (compt == 3) {
            return true;
        }
        compt = 0;
    }

    return false;
}

function isAlignedDiag(x) {
    if (x == startPosition[0][0] || x == startPosition[2][2] || x == startPosition[1][1])
        if (startPosition[1][1] == startPosition[0][0] && startPosition[1][1] == startPosition[2][2])
            return true;

    if (x == startPosition[0][2] || x == startPosition[2][0] || x == startPosition[1][1])
        if (startPosition[1][1] == startPosition[0][2] && startPosition[1][1] == startPosition[2][0])
            return true;

    return false;
}

function gameOver(x) {
    if (isAlignedX(x) || isAlignedY(x) || isAlignedDiag(x))
        return true;

    return false;
}