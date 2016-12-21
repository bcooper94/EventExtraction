import React, { Component } from 'react';
//import logo from './logo.svg';
import './App.css';


function Square(props) {
  return (
    <button className="square" onClick={() => props.onClick()}>
      {props.value}
    </button>
  );
}

class Board extends Component {
  renderSquare(i) {
    return <Square value={this.props.squares[i]} onClick={() => this.props.onClick(i)} />;
  }

  render() {
    let curColumns;
    let boardRows = [];

    for (var row = 0; row < 3; row++) {
      curColumns = [];
      for (var col = 0; col < 3; col++) {
        curColumns.push(this.renderSquare(3 * row + col));
      }

      boardRows.push(<div className="board-row">{curColumns}</div>);
    }
    return (<div>{boardRows}</div>);
  }
}

class Game extends Component {
  constructor() {
    super();
    this.state = {
      history: [{squares: Array(9).fill(null), move: null}],
      xIsNext: true,
      stepNumber: 0
    };
  }

  handleClick(i) {
    const history = this.state.history;
    const current = history[this.state.stepNumber];
    const squares = current.squares.slice();

    if (calculateWinner(squares) || squares[i]) {
      return;
    }

    squares[i] = this.state.xIsNext ? 'X' : 'O';
    this.setState({
      stepNumber: history.length,
      history: history.concat([{squares: squares, move: i}]),
      xIsNext: !this.state.xIsNext
    });
  }

  jumpTo(step) {
    this.setState({
      stepNumber: step,
      xIsNext: (step % 2) ? false : true
    });
  }

  reset() {
    this.setState({
      history: [{squares: Array(9).fill(null)}],
      xIsNext: true,
      stepNumber: 0
    });
  }

  render() {
    const history = this.state.history;
    const current = history[this.state.stepNumber];
    const winner = calculateWinner(current.squares);
    const moves = history.map((step, move) => {
      let desc, link, element;

      if (move > 0) {
        let row = Math.floor(step.move / 3) + 1, col = step.move % 3 + 1;
        desc = 'Move (' + row + ', ' + col + ')';
      }
      else{
        desc = 'Game Start';
      }

      link = (<a href="#" onClick={() => this.jumpTo(move)}>{desc}</a>);
      element = move == this.state.stepNumber ? (<strong>{link}</strong>) : link;

      return (<li key={move}>{element}</li>);
    });

    
    if (winner) {
      status = "Winner: " + winner;
    }
    else {
      status = "Next player: " + this.state.xIsNext ? "X" : "O";
    }

    return (
      <div className="game container">
        <div>
          <button className="btn btn-primary" onClick={() => this.reset()}>Reset</button>
        </div>
        <div className="game-board">
          <Board squares={current.squares}
            onClick={(i) => this.handleClick(i)}
          />
        </div>
        <div className="game-info">
          <div>{status}</div>
          <ol>{moves}</ol>
        </div>
      </div>
    );
  }
}

function calculateWinner(squares) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
  ];
  for (let i = 0; i < lines.length; i++) {
    const [a, b, c] = lines[i];
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
  }
  return null;
}

export default Game;
