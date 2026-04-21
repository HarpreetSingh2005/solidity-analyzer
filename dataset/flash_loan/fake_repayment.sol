// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Flash Loan Fake Repayment via Internal Accounting
 * CATEGORY: Flash Loan — Insufficient Repayment Validation
 *
 * The flash loan repayment check compares address(this).balance to a
 * snapshot taken before the loan — but the snapshot is taken AFTER
 * the receiver's callback runs. If the receiver deposits ETH back into
 * THIS contract (which increases address(this).balance), the repayment
 * check passes without the receiver actually sending ETH back.
 * The attacker satisfies the check using the vault's own internal balance.
 */
contract FakeRepayment {
    mapping(address => uint256) public deposits;
    uint256 public totalLiquidity;

    function deposit() external payable {
        deposits[msg.sender] += msg.value;
        totalLiquidity       += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(deposits[msg.sender] >= amount, "Insufficient");
        deposits[msg.sender] -= amount;
        totalLiquidity       -= amount;
        payable(msg.sender).transfer(amount);
    }

    function flashLoan(uint256 amount, address receiver) external {
        require(amount <= address(this).balance, "Insufficient");
        payable(receiver).transfer(amount);

        // BUG: snapshot taken AFTER transfer — receiver can call deposit()
        // to put money back into THIS contract and satisfy the check
        // without actually "repaying" in the economic sense
        uint256 expectedBalance = address(this).balance + amount; // wrong: should be pre-transfer balance
        (bool ok,) = receiver.call(abi.encodeWithSignature("executeOperation(uint256)", amount));
        require(ok, "Callback failed");

        // BUG: attacker called deposit() inside executeOperation() — balance is "restored"
        // but they've actually deposited THEIR OWN funds, not repaid the flash loan
        require(address(this).balance >= totalLiquidity, "Not repaid");
    }

    receive() external payable {}
}
