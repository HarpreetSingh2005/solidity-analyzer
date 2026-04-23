// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract FlashloanReentrancy {
    mapping(address => uint256) public deposits;
    function flashLoan(uint256 amount, address receiver) external {
        payable(receiver).transfer(amount);
        (bool ok,) = receiver.call(abi.encodeWithSignature("onFlashLoan(uint256)", amount));
        require(ok);
        require(address(this).balance >= amount, "Not repaid"); // BUG: reentrancy possible
    }
}