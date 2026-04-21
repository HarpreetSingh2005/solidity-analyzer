// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Cross-Function Reentrancy via Flash Loan
 * CATEGORY: Flash Loan — State Inconsistency Between Functions
 *
 * The reentrancy guard only blocks direct recursive calls to withdraw().
 * However, a flash loan callback can call a DIFFERENT function (borrow())
 * which also reads and writes the same state — before withdraw() updates it.
 * Classic pattern: withdraw → external call → borrow (not guarded) → double spend.
 */
contract CrossFuncReentrancy {
    mapping(address => uint256) public deposited;
    mapping(address => uint256) public borrowed;
    bool private _withdrawLocked;         // Only guards withdraw, not borrow

    function deposit() external payable {
        deposited[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(!_withdrawLocked, "Reentrant withdraw");
        require(deposited[msg.sender] >= amount, "Insufficient");
        _withdrawLocked = true;

        // External call before state update ← reentrancy point
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok, "Transfer failed");

        deposited[msg.sender] -= amount; // updated AFTER call
        _withdrawLocked = false;
    }

    // BUG: borrow() not guarded — can be called from within withdraw()'s callback
    function borrow(uint256 amount) external {
        // deposited[msg.sender] still shows old (pre-withdraw) balance here
        uint256 collateral = deposited[msg.sender];
        uint256 maxBorrow  = (collateral * 75) / 100;
        require(borrowed[msg.sender] + amount <= maxBorrow, "Over limit");
        borrowed[msg.sender] += amount;
        payable(msg.sender).transfer(amount);
    }

    receive() external payable {}
}
