<?php
defined( 'ABSPATH' ) || exit;
?>
	<footer class="bb-footer">
		<div class="bb-container bb-footer-grid">
			<div>
				<strong>BizBot</strong>
				<p class="bb-footer-tagline">Admin Tools Directory - Streamlining your business operations.</p>
			</div>
			<div>
				<strong><?php esc_html_e( 'Other directories', 'bizbot' ); ?></strong>
				<ul style="list-style:none;padding:0;margin:8px 0 0;">
					<li><a href="https://www.sales-leads-crm.com/" rel="noopener">Sales, Leads &amp; CRM tools</a></li>
					<li><a href="https://www.content-and-marketing.com/" rel="noopener">Content &amp; Marketing tools</a></li>
					<li><a href="https://bizbot.no/" rel="noopener">BizBot.no</a></li>
					<li><a href="https://work-smart-not-hard.tech/" rel="noopener">WorkSmart, NotHard</a></li>
				</ul>
			</div>
			<div>
				<strong><?php esc_html_e( 'Follow', 'bizbot' ); ?></strong>
				<ul style="list-style:none;padding:0;margin:8px 0 0;display:flex;gap:12px;">
					<li><a href="https://www.linkedin.com/" rel="noopener" aria-label="LinkedIn">LinkedIn</a></li>
					<li><a href="https://twitter.com/" rel="noopener" aria-label="Twitter">Twitter</a></li>
					<li><a href="https://www.facebook.com/" rel="noopener" aria-label="Facebook">Facebook</a></li>
				</ul>
			</div>
		</div>
	</footer>

<?php wp_footer(); ?>
</body>
</html>
