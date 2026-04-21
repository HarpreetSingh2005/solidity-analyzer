// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Test contract for Front-Running detection
// Pattern 1: ERC-20 approve() race condition
contract FrontRunning {
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    uint256 public totalSupply;

    constructor(uint256 initialSupply) {
        totalSupply = initialSupply;
        _balances[msg.sender] = initialSupply;
    }

    function balanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }

    // VULNERABLE: classic ERC-20 approve race condition
    // Spender can front-run this and spend both old + new allowance
    function approve(address spender, uint256 amount) public returns (bool) {
        _allowances[msg.sender][spender] = amount;
        return true;
    }

    function allowance(address owner, address spender) public view returns (uint256) {
        return _allowances[owner][spender];
    }

    // transferFrom confirms this is ERC-20 context
    function transferFrom(address from, address to, uint256 amount) public returns (bool) {
        require(_allowances[from][msg.sender] >= amount, "Allowance exceeded");
        _allowances[from][msg.sender] -= amount;
        _balances[from] -= amount;
        _balances[to] += amount;
        return true;
    }

    function transfer(address to, uint256 amount) public returns (bool) {
        require(_balances[msg.sender] >= amount, "Insufficient balance");
        _balances[msg.sender] -= amount;
        _balances[to] += amount;
        return true;
    }

    // VULNERABLE: payable + timestamp — Pattern 2
    // Miner can manipulate timestamp to determine flash sale winner
    function flashSale(uint256 saleEnd) public payable {
        require(block.timestamp < saleEnd, "Sale ended");
        require(msg.value >= 0.1 ether, "Min 0.1 ETH");
        // First buyer within the window wins tokens
        _balances[msg.sender] += 100;
    }
}
