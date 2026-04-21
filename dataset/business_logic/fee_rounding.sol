// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Fee Rounding-Down to Zero
 * CATEGORY: Business Logic — Integer Truncation Exploit
 *
 * Protocol charges a 0.3% fee. For any trade < 334 wei, the fee rounds
 * down to 0. An attacker can split a large trade into many tiny ones,
 * paying zero fees in total. Also: the fee recipient is set once and
 * never validated, so a malicious deployer can silently redirect fees.
 */
contract FeeRounding {
    uint256 public constant FEE_BPS = 30; // 0.30%
    address public feeRecipient;
    mapping(address => uint256) public balances;

    constructor(address _feeRecipient) {
        feeRecipient = _feeRecipient;
    }

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function swap(address to, uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient");
        // BUG: fee = amount * 30 / 10000 floors to 0 for amount < 334
        uint256 fee = (amount * FEE_BPS) / 10_000;
        uint256 net = amount - fee;

        balances[msg.sender] -= amount;
        balances[to]          += net;

        // BUG: if fee rounds to 0, feeRecipient receives nothing
        if (fee > 0) {
            balances[feeRecipient] += fee;
        }
    }

    function withdraw() external {
        uint256 bal = balances[msg.sender];
        balances[msg.sender] = 0;
        payable(msg.sender).transfer(bal);
    }

    receive() external payable {}
}
