// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe contract 32 implementing 2025 security patterns.
// @dev Uses CEI, custom errors, and safe arithmetic (native in 0.8+).
contract SafeNewContract32 {
    error InvalidAmount();
    error Unauthorized();
    error ReentrancyGuard();

    mapping(address => uint256) public balances;
    address public immutable owner;
    uint256 private _status;

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);

    modifier nonReentrant() {
        if (_status == 2) revert ReentrancyGuard();
        _status = 2;
        _;
        _status = 1;
    }

    constructor() {
        owner = msg.sender;
        _status = 1;
    }

    function deposit() external payable {
        if (msg.value == 0) revert InvalidAmount();
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external nonReentrant {
        if (amount == 0 || balances[msg.sender] < amount) revert InvalidAmount();
        
        // Effects
        balances[msg.sender] -= amount;
        
        // Interactions
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit Withdrawn(msg.sender, amount);
    }
}
