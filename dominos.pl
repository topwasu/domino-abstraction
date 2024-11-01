:- initialization(main, main).

will_tip(domino(X)) :-
    push(domino(X)),
    width(W), height(H),
    atom_concat('python3.11 will-tip.py ', W, Command1),
    atom_concat(Command1, ' ', Command2),
    atom_concat(Command2, H, Command),
    shell(Command, 0).

will_be_tipped(D) :- will_tip(D).

will_be_tipped(domino(X)) :-
    height(H),
    domino(X1),
    X1 < X,
    X - X1 =< H,
    will_be_tipped(domino(X1)).

will_be_tipped(domino(D)) :-
    ball_x(B),
    B < D,
    will_move_ball(ball_x(B)).

will_be_tipped_(D) :- once(will_be_tipped(D)).

will_move_ball(ball_x(B)) :-
    height(H),
    domino(X),
    X =< B,
    B - X =< H,
    will_be_tipped(domino(X)).

rightmost_ball(ball_x(B)) :-
    aggregate(max(XPos), ball_x(XPos), B).

rightmost_domino(domino(D)) :-
    aggregate(max(XPos), domino(XPos), D).

will_cup :-
    rightmost_ball(ball_x(B)),
    rightmost_domino(domino(D)),
    B > D,
    will_move_ball(ball_x(B)).

main :-
    ( will_cup -> halt(0) ; halt(1) ).
