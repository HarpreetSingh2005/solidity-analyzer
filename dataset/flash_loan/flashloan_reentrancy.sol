// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Flash Loan Reentrancy via Callback
 * CATEGORY: Flash Loan — Reentrancy During Flash Loan Execution
 *
 * The vault issues flash loans and calls onFlashLoan() on the receiver.
 * During that callback, the attacker re-enters withdraw() before
 * the balance is deducted at the end of flashLoan(). The vault's
 * internal balance tracking is not locked during the flash loan.
 */
contract FlashloanReentrancy {
    mapping(address => uint256) public deposits;
    uint256 public totalDeposits;
    bool    private _flashActive;

    function deposit() external payable {
        deposits[msg.sender] += msg.value;
        totalDeposits        += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(deposits[msg.sender] >= amount, "Insufficient");
        deposits[msg.sender] -= amount;
        totalDeposits        -= amount;
        payable(msg.sender).transfer(amount); // CEI: safe on its own
    }

    // BUG: no reentrancy guard — during callback, withdraw() is still callable
    function flashLoan(uint256 amount, address receiver, bytes calldata data) external {
        require(amount <= address(this).balance, "Insufficient liquidity");
        uint256 balBefore = address(this).balance;

        // External call to attacker-controlled receiver ← reentrancy entry point
        (bool ok,) = receiver.call{value: amount}(
            abi.encodeWithSignature("onFlashLoan(uint256,bytes)", amount, data)
        );
        require(ok, "Callback failed");

        // BUG: attacker called withdraw() inside onFlashLoan() — balance already reduced
        require(address(this).balance >= balBefore, "Flash loan not repaid");
    }

    receive() external payable {}
}
