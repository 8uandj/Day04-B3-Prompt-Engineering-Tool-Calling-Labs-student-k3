import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { ChatPanel } from "./ChatPanel";
import { copy } from "../i18n";

test("shows an optimistic question immediately and hides the empty state", () => {
  render(<ChatPanel copy={copy("vi")} session={null} busy pending="Câu hỏi đang gửi" onSend={vi.fn()}/>);
  expect(screen.getByText("Câu hỏi đang gửi")).toBeInTheDocument();
  expect(screen.queryByText("Bắt đầu bằng một câu hỏi nghiên cứu")).not.toBeInTheDocument();
});
